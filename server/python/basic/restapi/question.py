from handler import CustomHandler, Application
from util import inject

app: Application = inject(Application)

@app.GET("/api/test")
def test(handler: CustomHandler):
    return "Test"