from typing import Iterable, cast
from loguru import logger
from openai import OpenAI, Stream, NotGiven, NOT_GIVEN 
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionChunk,
    ChatCompletionMessageToolCall,
    ChatCompletion
)
from openai import Stream

from gptpaper.llm import call_with_functioncall

def main():
    """测试 call_with_functioncall 接口的多种场景"""
    
    # 测试数据准备
    base_messages: Iterable[ChatCompletionMessageParam] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather in Shanghai?"}
    ]
    
    weather_tool: ChatCompletionToolParam = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
    
    # 场景1: 无工具调用 (应返回None或Stream)
    print("\n=== 测试场景1: 无工具调用 ===")
    result1 = call_with_functioncall(base_messages)
    assert result1 is None or isinstance(result1, (Stream, list)), "场景1返回类型不符"
    logger.info(result1)

    # 场景2: 有工具但自动选择 (可能返回工具调用或Stream)
    print("\n=== 测试场景2: 有工具但自动选择 ===")
    result2 = call_with_functioncall(base_messages, tools=[weather_tool])
    assert result2 is None or isinstance(result2, (Stream, dict)), "场景2返回类型不符"

    result2 = cast(dict[int, ChatCompletionMessageToolCall], result2)
    logger.info(result2[0].id)
    logger.info(result2[0].function.name)
    logger.info(result2[0].function.arguments)

    # 场景3: 强制工具调用 (应返回工具调用列表)
    print("\n=== 测试场景3: 强制工具调用 ===")
    result3 = call_with_functioncall(
        base_messages,
        tools=[weather_tool],
        tool_choice={"type": "function", "function": {"name": "get_weather"}}
    )
    assert isinstance(result3, dict), "场景3应返回工具调用列表"
    logger.info(result3)
    
    logger.info("\n所有测试场景通过!")