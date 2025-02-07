"""Tests for event bus."""
import pytest
import asyncio
from src.events.bus import Event, EventBus

def test_event_bus_init(event_bus):
    """Test event bus initialization."""
    assert event_bus._subscribers == {}

@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    """Test publishing and subscribing to events."""
    bus = EventBus()
    received_events = []
    
    def handler(event):
        received_events.append(event)
    
    bus.subscribe('test_event', handler)
    event = Event('test_event', {'data': 'test'}, 'test')
    await bus.publish(event)
    
    assert len(received_events) == 1
    assert received_events[0].name == 'test_event'
    assert received_events[0].data == {'data': 'test'}

@pytest.mark.asyncio
async def test_event_bus_unsubscribe():
    """Test unsubscribing from events."""
    bus = EventBus()
    received_events = []
    
    def handler(event):
        received_events.append(event)
    
    bus.subscribe('test_event', handler)
    bus.unsubscribe('test_event', handler)
    event = Event('test_event', {'data': 'test'}, 'test')
    await bus.publish(event)
    
    assert len(received_events) == 0

def test_event_bus_clear_subscribers():
    """Test clearing subscribers."""
    bus = EventBus()
    
    def handler(event):
        pass
    
    bus.subscribe('test_event', handler)
    bus.clear_subscribers()
    assert bus._subscribers == {}
