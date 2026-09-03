class EventBus:
    """English: Single responsibility event publish subscribe / Single responsibility: event publish/subscribe / 单一职责：事件发布/订阅"""

    def __init__(self):
        self._handlers = {}

    def on(self, event, handler):
        """English: Subscribe to an event / Subscribe to an event / 订阅事件"""
        self._handlers.setdefault(event, []).append(handler)

    def off(self, event, handler=None):
        """English: Unsubscribe / Unsubscribe / 取消订阅"""
        if handler:
            handlers = self._handlers.get(event, [])
            self._handlers[event] = [h for h in handlers if h != handler]
        else:
            self._handlers.pop(event, None)

    def emit(self, event, **kwargs):
        """English: Emit an event / Emit an event / 触发事件"""
        for handler in self._handlers.get(event, []):
            handler(**kwargs)

    def once(self, event, handler):
        """English: Trigger only once / Trigger only once / 只触发一次"""

        def wrapper(**kwargs):
            handler(**kwargs)
            self.off(event, wrapper)

        self.on(event, wrapper)
