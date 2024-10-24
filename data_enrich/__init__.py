import azure.functions as func
import json
import traceback
import logging
from bson import ObjectId
from data_enrich import enrich




# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Handles incoming requests, processes queries, and constructs responses."""

    logging.info("search handler endpoint triggered")

    try:
        req_body = req.get_json()
        logging.info(f"Incoming Request - {req_body}")
        candidate_id = req_body["candidate_id"]
        response = enrich.process(id=candidate_id)
        
        logging.info(response)

        return func.HttpResponse(
            body=json.dumps(response,cls=JSONEncoder),
            mimetype="application/json",
            status_code=200,
        )

    except Exception as ex:
        logging.exception(traceback.format_exc())
        return func.HttpResponse(
            body=json.dumps({"response": str(ex)}),
            mimetype="application/json",
            status_code=400,
        )
