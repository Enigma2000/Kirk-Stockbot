class ContextList:
    def __init__(self, contexts=[]):
        self.contexts = []

    def add(self, context):
        self.contexts.append(context)

    def empty(self):
        self.contexts = []

    async def send(self, content, embed=None):
        for context in self.contexts:
            await context.send(content, embed=embed)