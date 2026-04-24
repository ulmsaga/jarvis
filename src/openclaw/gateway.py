"""Openclaw 오케스트레이터 — 전체 6단계 사이클"""
import time
from pathlib import Path
from src.openclaw import brain, skills, memory
from src.config import settings


async def handle(
    user_message: str,
    channel_id: str,
    user_id: str,
    thread_ts: str | None = None,
) -> str:
    session_id = f"{channel_id}:{user_id}"
    started = time.time()

    # Step 2: Brain — 작업 분해
    history = await memory.get_history(session_id)
    decision = await brain.decide(user_message, history)

    skill_name: str = decision.get("skill", "unknown")
    repo: str = decision.get("repo", "")
    branch: str = decision.get("branch", "main")
    target: str = decision.get("target", user_message)
    reviewers: list[str] = decision.get("reviewers", [])

    # help / unknown은 즉시 응답
    if skill_name in ("help", "unknown"):
        result = await skills.run(skill_name, target)
        await _save(session_id, channel_id, user_id, user_message, result)
        return result

    worktree: Path | None = None
    pr_info: dict = {}

    # Step 3: Git Clone (워크트리 격리)
    if repo and settings.github_token:
        try:
            from src.openclaw import worktree as wt
            worktree = wt.clone(repo, branch)
        except Exception as e:
            return f"❌ Git Clone 실패 (`{repo}@{branch}`): {e}"

    # Step 4: Claude Code 스킬 실행
    try:
        report = await skills.run(skill_name, target, worktree)
    except Exception as e:
        _cleanup(worktree)
        return f"❌ 스킬 실행 실패: {e}"

    # Step 5: PR 생성
    if worktree and repo and settings.github_token:
        try:
            from src.openclaw import git_agent
            pr_info = await git_agent.commit_and_pr(
                worktree=worktree,
                repo_name=repo,
                base_branch=branch,
                skill_name=skill_name,
                report=report,
                reviewers=reviewers,
            )
        except Exception as e:
            pr_info = {"error": str(e)}
        finally:
            _cleanup(worktree)

    # Step 6: Slack 응답 조합
    elapsed = time.time() - started
    response = _format(skill_name, report, pr_info, reviewers, elapsed)

    await _save(session_id, channel_id, user_id, user_message, response)
    return response


def _cleanup(worktree: Path | None) -> None:
    if worktree:
        from src.openclaw import worktree as wt
        wt.cleanup(worktree)


async def _save(session_id: str, channel_id: str, user_id: str, user_msg: str, reply: str) -> None:
    await memory.append_history(session_id, channel_id, user_id, "user", user_msg)
    await memory.append_history(session_id, channel_id, user_id, "assistant", reply)


def _format(skill: str, report: str, pr_info: dict, reviewers: list[str], elapsed: float) -> str:
    mins, secs = divmod(int(elapsed), 60)
    time_str = f"{mins}분 {secs}초" if mins else f"{secs}초"

    lines = [f"✅ *{skill}* 완료 · {time_str} 소요"]

    if pr_info.get("pr_url"):
        lines.append(f"📎 PR #{pr_info['pr_number']}: {pr_info['pr_url']}")
    elif pr_info.get("changed") is False:
        lines.append("ℹ️ 변경사항 없음 — PR 생성 생략")
    elif pr_info.get("error"):
        lines.append(f"⚠️ PR 생성 실패: {pr_info['error']}")

    if reviewers:
        lines.append(f"👥 리뷰 요청: {' '.join(reviewers)}")

    lines.append(f"\n```\n{report[:1800]}\n```")
    return "\n".join(lines)
