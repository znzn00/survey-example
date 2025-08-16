from handler import CustomHandler, app as app

@app.GET("/api/test")
def test(handler: CustomHandler):
    return "Test"