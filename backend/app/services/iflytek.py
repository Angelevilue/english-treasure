"""
讯飞语音评测 API 集成 (ISE — English Speaking Evaluation)

文档: https://www.xfyun.cn/doc/ise/Ise-API.html
协议: WebSocket
评测模式: read_sentence (句子跟读)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from urllib.parse import urlencode

import httpx

from app.core.config import settings


class IFlytekSpeechEvaluator:
    """讯飞语音评测 WebSocket 封装"""

    BASE_URL = "wss://ise-api.xfyun.cn/v2/open-ise"

    def __init__(self):
        self.app_id = settings.IFLYTEK_APP_ID
        self.api_key = settings.IFLYTEK_API_KEY
        self.api_secret = settings.IFLYTEK_API_SECRET

    def _build_auth_params(self) -> tuple[str, str, str]:
        """构建鉴权参数，返回 (url, auth_header, date)"""
        host = "ise-api.xfyun.cn"
        path = "/v2/open-ise"
        now = datetime.utcnow()
        date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode(),
            signature_origin.encode(),
            digestmod=hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_sha).decode()

        authorization = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        encoded_auth = base64.b64encode(authorization.encode()).decode()

        url = f"wss://{host}{path}?{urlencode({'authorization': encoded_auth, 'date': date, 'host': host})}"
        return url, authorization, date

    async def evaluate_sentence(
        self,
        audio_base64: str,
        text: str,
    ) -> dict:
        """
        评测单句跟读（通过 WebSocket）。

        Args:
            audio_base64: 录音的 base64 编码
            text: 参考文本（用户应读的句子）

        Returns:
            评测结果 dict
        """
        import websockets

        url = self._build_auth_url()
        result = {}

        try:
            async with websockets.connect(url, additional_headers={
                "Content-Type": "application/json",
            }) as ws:
                # 第一步：发送请求参数
                request_params = {
                    "common": {"app_id": self.app_id},
                    "business": {
                        "category": "read_sentence",
                        "ent": "en_vip",
                        "text": text,
                        "rst": "cn",
                    },
                    "data": {
                        "status": 0,  # 第一帧
                        "format": "audio/wav",
                        "encoding": "raw",
                        "audio": "",
                    },
                }
                await ws.send(json.dumps(request_params))

                # 等待服务端确认
                response = await ws.recv()
                resp_data = json.loads(response)

                if resp_data.get("code") != 0:
                    return {"error": f"讯飞初始化失败: {resp_data.get('message', resp_data)}"}

                # 第二步：发送音频数据
                audio_params = {
                    "data": {
                        "status": 2,  # 最后一帧
                        "format": "audio/wav",
                        "encoding": "raw",
                        "audio": audio_base64,
                    }
                }
                await ws.send(json.dumps(audio_params))

                # 第三步：接收评测结果
                final_response = await ws.recv()
                final_data = json.loads(final_response)

                result = self._parse_result(final_data)

        except Exception as e:
            return {"error": f"讯飞评测异常: {str(e)}"}

        return result

    def _parse_result(self, raw: dict) -> dict:
        """解析讯飞评测原始响应为标准格式。"""
        try:
            data = raw.get("data", {})

            # 总分
            overall = data.get("total_score", 0)
            accuracy = 0
            fluency = 0
            completeness = 0

            # 解析朗读结果
            read_info = data.get("read_chapter", {})
            if read_info:
                overall = read_info.get("total_score", overall)

            # 分维度分数
            read_sentence = data.get("read_sentence", {})
            if not read_sentence and "rec_paper" in data:
                rec = data["rec_paper"]
                if "read_chapter" in rec:
                    chap = rec["read_chapter"]
                    accuracy = chap.get("accuracy_score", 0)
                    fluency = chap.get("fluency_score", 0)
                    completeness = chap.get("integrity_score", 0)

            # 单词级诊断
            words_detail = []
            if "rec_paper" in data and "read_chapter" in data["rec_paper"]:
                chap = data["rec_paper"]["read_chapter"]
                for sent in chap.get("sentences", []):
                    for w in sent.get("words", []):
                        words_detail.append({
                            "word": w.get("content", ""),
                            "score": w.get("total_score", 0),
                            "phonemes": w.get("syll", []),
                        })

            return {
                "overall_score": float(overall),
                "accuracy_score": float(accuracy) if accuracy else float(overall) * 0.33,
                "fluency_score": float(fluency) if fluency else float(overall) * 0.33,
                "completeness_score": float(completeness) if completeness else float(overall) * 0.34,
                "words": words_detail if words_detail else None,
            }

        except Exception as e:
            return {
                "overall_score": 0,
                "accuracy_score": 0,
                "fluency_score": 0,
                "completeness_score": 0,
                "parse_error": str(e),
                "raw": str(raw)[:500],
            }


# 单例
evaluator = IFlytekSpeechEvaluator()
