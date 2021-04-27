import asyncio
import threading
from aiohttp import web


class Web:
    def __init__(self):
        self.thread = threading.Thread(
            target=self._run_server, args=(self._server(),), daemon=True)

    def __enter__(self):
        self.thread.start()

    def __exit__(self, type, value, traceback):
        self.thread.join(0)
    
    def _run_server(self, runner):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, '0.0.0.0', 5000)
        loop.run_until_complete(site.start())
        loop.run_forever()

    def _server(self):
        def health(request):
            return web.Response(text='OK')

        app = web.Application()
        app.add_routes([web.get('/health', health)])
        runner = web.AppRunner(app)
        return runner
