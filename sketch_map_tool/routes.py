import json

# from functools import reduce
from io import BytesIO
from uuid import uuid4

import geojson

# from celery import chain, group
from flask import Response, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from sketch_map_tool import celery_app, definitions
from sketch_map_tool import flask_app as app
from sketch_map_tool import tasks
from sketch_map_tool.database import client as db_client
from sketch_map_tool.definitions import REQUEST_TYPES
from sketch_map_tool.exceptions import (
    MapGenerationError,
    OQTReportError,
    QRCodeError,
    UUIDNotFoundError,
)
from sketch_map_tool.models import Bbox, PaperFormat, Size
from sketch_map_tool.validators import validate_type, validate_uuid


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/help")
def help() -> str:
    return render_template("help.html")


@app.get("/about")
def about() -> str:
    return render_template("about.html", literature=definitions.LITERATURE_REFERENCES)


@app.get("/create")
def create() -> str:
    """Serve forms for creating a sketch map"""
    return render_template("create.html")


@app.post("/create/results")
def create_results_post() -> Response:
    """Create the sketch map"""
    # Request parameters
    bbox_raw = json.loads(request.form["bbox"])
    bbox_wgs84_raw = json.loads(request.form["bboxWGS84"])
    bbox = Bbox(*bbox_raw)
    bbox_wgs84 = Bbox(*bbox_wgs84_raw)
    format_raw = request.form["format"]
    format_: PaperFormat = getattr(definitions, format_raw.upper())
    orientation = request.form["orientation"]
    size_raw = json.loads(request.form["size"])
    size = Size(**size_raw)
    scale = float(request.form["scale"])

    # Unique id for current request
    uuid = str(uuid4())

    # Tasks
    task_sketch_map = tasks.generate_sketch_map.apply_async(
        args=(uuid, bbox, format_, orientation, size, scale)
    )
    task_quality_report = tasks.generate_quality_report.apply_async(args=(bbox_wgs84,))

    # Map of request type to multiple Async Result IDs
    map_ = {
        "sketch-map": str(task_sketch_map.id),
        "quality-report": str(task_quality_report.id),
    }
    db_client.set_async_result_ids(uuid, map_)
    return redirect(url_for("create_results_get", uuid=uuid))


@app.get("/create/results")
@app.get("/create/results/<uuid>")
def create_results_get(uuid: str | None = None) -> Response | str:
    if uuid is None:
        return redirect(url_for("create"))
    validate_uuid(uuid)
    # Check if celery tasks for UUID exists
    _ = db_client.get_async_result_id(uuid, "sketch-map")
    _ = db_client.get_async_result_id(uuid, "quality-report")
    return render_template("create-results.html")


@app.get("/digitize")
def digitize() -> str:
    """Serve a file upload form for sketch map processing"""
    return render_template("digitize.html")


@app.post("/digitize/results")
def digitize_results_post() -> Response:
    """Upload files to create geodata results"""
    # No files uploaded
    if "file" not in request.files:
        return redirect(url_for("digitize"))
    # TODO FileStorage seems not to be serializable -> Error too much Recursion
    # the map function transforms the list of FileStorage Objects to a list of bytes
    # not sure if this is the best approach but is accepted by celery task
    # if we want the filenames we must construct a list of tuples or dicts
    # TODO: Write files to database
    files = request.files.getlist("file")
    id_ = tasks.generate_digitized_results(
        [(BytesIO(file.read()), secure_filename(file.filename)) for file in files]
    )
    return redirect(url_for("digitize_results_get", uuid=id_))


@app.get("/digitize/results")
@app.get("/digitize/results/<uuid>")
def digitize_results_get(uuid: str | None = None) -> Response | str:
    if uuid is None:
        return redirect(url_for("digitize"))
    validate_uuid(uuid)
    return render_template("digitize-results.html")


@app.get("/api/status/<uuid>/<type_>")
def status(uuid: str, type_: REQUEST_TYPES) -> Response:
    validate_uuid(uuid)
    validate_type(type_)

    id_ = db_client.get_async_result_id(uuid, type_)
    task = celery_app.AsyncResult(id_)

    href = None
    error = None
    if task.ready():
        if task.successful():  # SUCCESS
            http_status = 200
            status = "SUCCESSFUL"
            href = "/api/download/" + uuid + "/" + type_
        elif task.failed():  # REJECTED, REVOKED, FAILURE
            try:
                task.get(propagate=True)
            except MapGenerationError as err:
                http_status = 408  # Request Timeout
                status = "FAILED"
                error = str(err)
            except (QRCodeError, OQTReportError) as err:
                # The request was well-formed but was unable to be followed due to semantic
                # errors.
                http_status = 422  # Unprocessable Entity
                status = "FAILED"
                error = str(err)
            except (Exception) as err:
                http_status = 500  # Internal Server Error
                status = "FAILED"
                error = str(err)
    else:  # PENDING, RETRY, RECEIVED, STARTED
        # Accepted for processing, but has not been completed
        http_status = 202  # Accepted
        status = "PROCESSING"
    body_raw = {
        "id": uuid,
        "status": status,
        "type": type_,
        "href": href,
        "error": error,
    }
    body = {k: v for k, v in body_raw.items() if v is not None}
    return Response(json.dumps(body), status=http_status, mimetype="application/json")


@app.route("/api/download/<uuid>/<type_>")
def download(uuid: str, type_: REQUEST_TYPES) -> Response:
    validate_uuid(uuid)
    validate_type(type_)

    id_ = db_client.get_async_result_id(uuid, type_)
    task = celery_app.AsyncResult(id_)

    match type_:
        case "quality-report":
            mimetype = "application/pdf"
            download_name = type_ + ".pdf"
            if task.successful():
                file: BytesIO = task.get()
        case "sketch-map":
            mimetype = "application/pdf"
            download_name = type_ + ".pdf"
            if task.successful():
                file: BytesIO = task.get()[0]  # return only the sketch map
        case "raster-results":
            mimetype = "application/zip"
            download_name = type_ + ".zip"
            if task.successful():
                file = task.get()
        case "vector-results":
            mimetype = "application/geo+json"
            download_name = type_ + ".geojson"
            if task.successful():
                file = BytesIO(geojson.dumps(task.get()).encode("utf-8"))
    return send_file(file, mimetype, download_name=download_name)


@app.errorhandler(QRCodeError)
def handle_exception(error):
    return render_template("error.html", error_msg=str(error)), 422


@app.errorhandler(UUIDNotFoundError)
def handle_not_found_exception(error):
    return render_template("error.html", error_msg=str(error)), 404
