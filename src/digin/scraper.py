import asyncio
import hashlib
import random
import re
import time

from playwright.async_api import Page, async_playwright

from digin.config import Config
from digin.models import Post


async def scrape_saved_posts(config: Config, max_posts: int | None = None) -> list[Post]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=config.headless)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.linkedin.com/login")
        print("Please log in to LinkedIn. The tool will continue automatically once you reach your saved posts.")

        if not await _wait_for_saved_posts_page(page):
            print("Timed out waiting for login. Exiting.")
            await browser.close()
            return []

        print("Login detected! Navigating to saved posts...")
        await page.goto("https://www.linkedin.com/my-items/saved-posts/")
        await page.wait_for_load_state("networkidle")

        posts = await _scroll_and_extract(page, config, max_posts)

        await browser.close()
        return posts


async def _wait_for_saved_posts_page(page: Page, timeout_seconds: int = 300) -> bool:
    start = time.time()
    while time.time() - start < timeout_seconds:
        url = page.url
        if "/login" not in url and "linkedin.com" in url:
            return True
        await asyncio.sleep(2)
    return False


async def _scroll_and_extract(
    page: Page, config: Config, max_posts: int | None
) -> list[Post]:
    posts: list[Post] = []
    seen_ids: set[str] = set()
    no_new_count = 0

    while True:
        elements = await _get_post_elements(page)

        found_new = False
        for elem in elements:
            if max_posts and len(posts) >= max_posts:
                return posts

            post = await _extract_post(elem)
            if post and post.id not in seen_ids:
                seen_ids.add(post.id)
                posts.append(post)
                found_new = True

        if not found_new:
            no_new_count += 1
            if no_new_count >= config.max_scroll_attempts:
                break
        else:
            no_new_count = 0

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        delay = config.scroll_delay + random.uniform(0, 1)
        await asyncio.sleep(delay)

        print(f"  Scraped {len(posts)} posts so far...")

    return posts


async def _get_post_elements(page: Page) -> list:
    selectors = [
        "[data-urn*='urn:li:activity']",
        ".feed-shared-update-v2",
        ".occludable-update",
    ]
    for selector in selectors:
        elements = await page.query_selector_all(selector)
        if elements:
            return elements
    return []


async def _extract_post(elem) -> Post | None:
    try:
        post_id = await elem.get_attribute("data-urn") or await elem.get_attribute("data-id")
        if not post_id:
            text = await elem.inner_text()
            post_id = hashlib.md5(text[:100].encode()).hexdigest()

        url = f"https://www.linkedin.com/feed/update/{post_id}" if "urn:li:" in (post_id or "") else ""

        author = await _try_selectors(elem, [
            ".feed-shared-actor__name",
            ".update-components-actor__name",
        ])

        author_profile = ""
        try:
            actor_link = await elem.query_selector(".feed-shared-actor__container a, .update-components-actor a")
            if actor_link:
                author_profile = await actor_link.get_attribute("href") or ""
        except Exception:
            pass

        content = await _try_selectors(elem, [
            ".feed-shared-text",
            ".update-components-text",
        ])

        post_type = await _detect_post_type(elem)
        engagement = await _extract_engagement(elem)
        links = await _extract_links(elem)

        from datetime import datetime, timezone

        return Post(
            id=post_id,
            url=url,
            author=author or "Unknown",
            author_profile=author_profile,
            content=content or "",
            post_type=post_type,
            saved_at=datetime.now(timezone.utc),
            engagement=engagement,
            links=links,
            cluster_id=None,
        )
    except Exception as e:
        print(f"  Warning: failed to extract post: {e}")
        return None


async def _try_selectors(elem, selectors: list[str]) -> str:
    for selector in selectors:
        try:
            el = await elem.query_selector(selector)
            if el:
                return (await el.inner_text()).strip()
        except Exception:
            continue
    return ""


async def _detect_post_type(elem) -> str:
    checks = [
        (".feed-shared-article, .update-components-article", "article"),
        ("video, .feed-shared-linkedin-video", "video"),
        (".feed-shared-image, .update-components-image", "image"),
    ]
    for selector, ptype in checks:
        try:
            el = await elem.query_selector(selector)
            if el:
                return ptype
        except Exception:
            continue
    return "text"


async def _extract_engagement(elem) -> dict:
    engagement = {"likes": 0, "comments": 0}
    try:
        social = await elem.query_selector(".social-details-social-counts")
        if social:
            text = await social.inner_text()
            likes_match = re.search(r"([\d,]+)\s*(?:like|reaction)", text, re.IGNORECASE)
            comments_match = re.search(r"([\d,]+)\s*comment", text, re.IGNORECASE)
            if likes_match:
                engagement["likes"] = int(likes_match.group(1).replace(",", ""))
            if comments_match:
                engagement["comments"] = int(comments_match.group(1).replace(",", ""))
    except Exception:
        pass
    return engagement


async def _extract_links(elem) -> list[str]:
    links = []
    try:
        anchors = await elem.query_selector_all(".feed-shared-text a, .update-components-text a")
        for a in anchors:
            href = await a.get_attribute("href")
            if href and not href.startswith("#"):
                links.append(href)
    except Exception:
        pass
    return links
