# main.py

import httpx
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    name="daily_news",
    author="kuank",
    desc="一个在用户输入'/新闻'时，提供每日新闻的插件",
    version="1.0.0",
    repo_url="https://github.com/kuankqaq/astrbot_news"
)
class NewsPlugin(Star):
    """
    每日新闻插件，响应'/新闻'指令。
    """

    def __init__(self, context: Context):
        super().__init__(context)
        # 遵循文档建议，使用异步库进行网络请求
        self.http_client = httpx.AsyncClient()

    @filter.command("新闻")
    async def get_daily_news(self, event: AstrMessageEvent):
        """这是一个获取每日60秒新闻的指令"""
        news_url = "https://60s.viki.moe/v2/60s?encoding=text"
        try:
            # 发起异步GET请求
            response = await self.http_client.get(news_url, timeout=15.0)
            # 如果请求失败（如404, 500等），则抛出异常
            response.raise_for_status()
            news_content = response.text
            # 使用yield发送纯文本消息
            yield event.plain_result(news_content)
        except httpx.RequestError as e:
            logger.error(f"请求新闻URL失败: {e}")
            yield event.plain_result("抱歉，获取新闻失败了，请稍后再试。")
        except Exception as e:
            logger.error(f"处理新闻时发生未知错误: {e}")
            yield event.plain_result("抱歉，插件出了一点问题，请联系管理员。")

    async def terminate(self):
        """当插件被卸载或停用时调用，用于资源清理。"""
        if not self.http_client.is_closed:
            await self.http_client.aclose()
        logger.info("新闻插件已停用，网络客户端已关闭。")