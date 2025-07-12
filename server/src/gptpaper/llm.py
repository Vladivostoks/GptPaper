import os
from typing import Iterable
from dotenv import load_dotenv

from loguru import logger
from openai import OpenAI, Stream, NotGiven, NOT_GIVEN 
from openai.types.chat import (ChatCompletionMessageToolCall, 
                               ChatCompletionToolParam, 
                               ChatCompletionChunk, 
                               ChatCompletionMessageParam, 
                               ChatCompletionToolChoiceOptionParam,
                               ChatCompletion)
from openai.types.chat.chat_completion_message_tool_call import Function

# 加载.env文件中的配置
load_dotenv()

def handle_stream_response(stream:Stream[ChatCompletionChunk])->Stream[ChatCompletionChunk]|dict[int,ChatCompletionMessageToolCall]|None:
    tool_calls:dict[int,ChatCompletionMessageToolCall]={}
    
    for chunk in stream:
        if not chunk.choices:
            continue
            
        delta = chunk.choices[0].delta
        
        # 不处理文本内容
        if delta.content and len(delta.content)>0:
            return stream
        # 处理工具调用
        elif delta.tool_calls:
            for tool_call in delta.tool_calls:
                index = tool_call.index
                if index not in tool_calls.keys():
                    tool_calls[index] = ChatCompletionMessageToolCall(
                        id         = "",
                        function   = Function(
                            name        = "",
                            arguments   = "",
                        ),
                        type   =    "function"
                    )

                # 更新ID
                if tool_call.id:
                    tool_calls[index].id = tool_call.id
                
                # 更新函数名
                if tool_call.function and tool_call.function.name:
                    tool_calls[index].function.name = tool_call.function.name
                
                # 更新参数
                if tool_call.function and tool_call.function.arguments:
                    tool_calls[index].function.arguments += tool_call.function.arguments
        
        # 空role表示响应结束
        elif chunk.choices[0].finish_reason:
            return tool_calls
    # 处理未完成的工具调用（如果流意外结束）#TODO:报错提示意外中断原因
    return None

# 创建客户端（从环境变量读取配置）
client = OpenAI(
    # api_key=os.getenv("OPENAI_API_KEY", "sk-567d0d45c7c149729a388ffc21203601"),
    # base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
    api_key="sk-567d0d45c7c149729a388ffc21203601",
    base_url="https://api.deepseek.com",
    timeout=3000,
)

def call_with_functioncall(messages     :Iterable[ChatCompletionMessageParam], 
                           tools        :Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN, 
                           tool_choice  :ChatCompletionToolChoiceOptionParam='auto',
                           is_stream    :bool=True)->Stream[ChatCompletionChunk]|dict[int,ChatCompletionMessageToolCall]|ChatCompletion|None:
    try:
        # 流式调用
        if is_stream:
            with client.chat.completions.create(
                model       = os.getenv("OPENAI_CHAT_MODEL", "deepseek-chat"),
                stream      = True,
                messages    = messages,
                max_tokens  = int(os.getenv("MODEL_MAX_TOKENS", "2048")),
                temperature = float(os.getenv("MODEL_TEMPERATURE", "0.7")),
                tools       = tools,
                tool_choice = tool_choice,
            ) as stream:
                return handle_stream_response(stream)
        else:
            message:ChatCompletion = client.chat.completions.create(
                model       = os.getenv("OPENAI_CHAT_MODEL", "deepseek-chat"),
                stream      = False,
                messages    = messages,
                max_tokens  = int(os.getenv("MODEL_MAX_TOKENS", "2048")),
                temperature = float(os.getenv("MODEL_TEMPERATURE", "0.7")),
                tools       = tools,
                tool_choice = tool_choice,
            )

            return message
    except Exception as e:
        logger.exception(e)
