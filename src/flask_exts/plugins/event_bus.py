class EventBus:
    """单一职责：事件发布/订阅"""

    def __init__(self):
        self._handlers = {}

    def on(self, event, handler):
        """订阅事件"""
        self._handlers.setdefault(event, []).append(handler)

    def off(self, event, handler=None):
        """取消订阅"""
        if handler:
            handlers = self._handlers.get(event, [])
            self._handlers[event] = [h for h in handlers if h != handler]
        else:
            self._handlers.pop(event, None)

    def emit(self, event, **kwargs):
        """触发事件"""
        for handler in self._handlers.get(event, []):
            handler(**kwargs)

    def once(self, event, handler):
        """只触发一次"""

        def wrapper(**kwargs):
            handler(**kwargs)
            self.off(event, wrapper)

        self.on(event, wrapper)
