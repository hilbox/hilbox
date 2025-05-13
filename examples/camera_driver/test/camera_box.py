from box import Box

class CameraBox(Box):
    async def capture(self):
        return await self.call("capture")

    async def set_color(self, r,g,b):
        return await self.call("set_color", {"c":[r,g,b]})
