from fastapi import APIRouter
from fastapi.responses import StreamingResponse
# from app.data.messages.chat import ChatRequest, ChatResponse
from app.rag_server import ask_chat,ask_stream_chat
from pydantic import Field, BaseModel
import logging
from llama_index.llms.base import ChatMessage
from llama_index.core.llms.types import MessageRole
# from app.data.models.mongodb import Message

chatbot_router = APIRouter(
    prefix="/chat",
    tags=["chatbot"],
)

# class ChatRequest:
#     conversation_id:str
#     content:str


# class ChatResponse:
#     def __init__(self, data) -> None:
#         self.data = data

class Message(BaseModel):
    conversation_id: str = Field(..., description="Unique id of the conversation")
    role: MessageRole = Field(..., description="Author of the chat message")
    content: str = Field(..., description="Content of the chat message")
    timestamp: int = Field(..., description="Time when this chat message was sent, in milliseconds")
    # time: str] = Field(None, description="Time when this chat message was sent, in human readable format")

class ChatRequest(BaseModel):
    conversation_id: str = Field(..., description="Unique id of the conversation")
    content: str = Field(..., description="Content of the chat message")

    def to_chat_message(self) -> ChatMessage:
        return ChatMessage(
            role=MessageRole.USER,
            content=self.content,
        )


class ChatResponse(BaseModel):
    # data: Message = Field(..., description="response from the chatbot")
    data: str = Field(..., description="response from the chatbot")


logger = logging.getLogger(__name__)


@chatbot_router.post(
    "/non-streaming",
    response_model=ChatResponse,
    description="Chat with the ai bot in a non streaming way.")
async def chat(request: ChatRequest):
    logger.info("Non streaming chat")
    conversation_id = request.conversation_id
    message = ask_chat(request.content, conversation_id)
    return ChatResponse(data=message)


@chatbot_router.post(
    "/streaming",
    description="Chat with the ai bot in a streaming way."
)
async def streaming_chat(request: ChatRequest):
    logger.info("streaming chat")
    conversation_id = request.conversation_id
    return StreamingResponse(
        ask_stream_chat(request.content, conversation_id),
        media_type='text/event-stream'
    )