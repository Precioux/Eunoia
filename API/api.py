# Import FastAPI and pydantic
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, ORJSONResponse#, PrettyJSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from model import NLUModel
import uvicorn
import json


import json, typing
from starlette.responses import Response

class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")


# http://localhost:8090/predict?text=

# Create an app instance
app = FastAPI()

nlu_model = NLUModel()

# class Item(BASEModel):



@app.get("/predict", response_class=PrettyJSONResponse)   #JSONResponse  or  PrettyJSONResponse
async def predict(conversation: str, turn: str):
    # Call the inference function and get the output data
    output_conversation = nlu_model.inference(conversation)
    output_turn = nlu_model.inference(turn)
    print(output_turn)
    whatever_flag = False
    if output_turn['intent']['label'] == 'whatever':
        whatever_flag = True
    output = {'conversation' : output_conversation, 'whatever' : whatever_flag}
    return output
    # Return the output data as JSON
    # return JSONResponse(json.dumps(output))
    # output = json.loads(str(output))
    # output = jsonable_encoder(output)
    # return JSONResponse(content=output.json())
    # output = jsonable_encoder(output)
    # return JSONResponse(content=output , media_type="application/json")
    # json_output = jsonable_encoder(output)
    # return JSONResponse(json_output)
    # return jsonable_encoder(output)

if __name__ == "__main__":
    # Run the app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8092)