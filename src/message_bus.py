import time
import threading
import logging
from typing import List, Optional

logger = logging.getLogger("message_bus")

class MessagePayload:
    """
    Defines a structured payload used by agents to communicate via MessageBus.
    """
    def __init__(
        self,
        sender_id: str,
        content: str,
        receiver_id: Optional[str] = None,
        timestamp: float = None
    ):
        self.sender_id = sender_id
        self.receiver_id = receiver_id  # If None, considers broadcast
        self.content = content
        self.timestamp = timestamp if timestamp else time.time()

    def __repr__(self):
        receiver = self.receiver_id if self.receiver_id else "ALL"
        text = self.content[:30] + ("..." if len(self.content) > 30 else "")
        return f"<Message from {self.sender_id} to {receiver}: {text}>"

class MessageBus:
    """
    A global or shared message bus that agents use to publish/subscribe messages.
    Thread-safe for concurrent usage.
    """
    def __init__(self):
        self.messages: List[MessagePayload] = []
        self.lock = threading.Lock()

    def publish(self, message: MessagePayload):
        """
        Publish a message to the bus.
        """
        with self.lock:
            self.messages.append(message)
        logger.info(f"Message published: {message}")

    def fetch_all(self) -> List[MessagePayload]:
        """
        Retrieve and clear all messages currently on the bus.
        """
        try:
            with self.lock:
                current_messages = self.messages[:]
                self.messages.clear()
                return current_messages
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []