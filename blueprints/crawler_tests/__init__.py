# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Module serving all the traffic for javascript test cases."""
import os
from flask import abort
from flask import Blueprint
from flask import make_response
from flask import render_template
from flask import Response
from flask import send_from_directory
from flask import url_for
from flask import request

crawler_tests = Blueprint(
    "crawler_tests", __name__, template_folder="templates")

# Global app.instance_path is not accessible from blueprints ¯\_(ツ)_/¯.
TEST_CASES_PATH = os.path.abspath(__file__ + "/../../../test-cases/crawler_tests/")


@crawler_tests.route("/infinity_app/in_param/")
def in_param_index():
  try:
    path = int(request.args.get('path'))
  except Exception as e:
    path = 1

  return render_template("infinity_site.html", path=path,
                         next_url="in_param?path={}".format(path+1),
                         prev_url="in_param?path={}".format(path-1),
                         interesting_url="in_param/interesting_url.found",
                         )


@crawler_tests.route("/infinity_app/in_path/")
@crawler_tests.route("/infinity_app/in_path/<string:path>")
def in_path_index(path):
  try:
    path = int(path)
  except Exception as e:
    path = 1

  return render_template("infinity_site.html", path=path,
                         next_url="in_path/{}".format(path+1),
                         prev_url="in_path/{}".format(path-1),
                         interesting_url="in_path/interesting_url.found",
                         )


@crawler_tests.route("/ajax_query/hidden_call/")
def hidden_call():
  return render_template("hidden_call.html", ajax_path="hidden_call/interesting_url.found")


@crawler_tests.route("/ajax_query/after_click/")
def after_click():
  return render_template("hidden_ajax_after_click.html", ajax_path="after_click/interesting_url.found")


@crawler_tests.route("/ajax_query/hidden_call/interesting_url.found")
@crawler_tests.route("/ajax_query/after_click/interesting_url.found")
@crawler_tests.route("/infinity_app/in_param/interesting_url.found")
@crawler_tests.route("/infinity_app/in_path/interesting_url.found")
def interesting_url_found():
  return make_response("passed", 200)


@crawler_tests.route("/", defaults={"path": ""})
@crawler_tests.route("/<path:path>")
def html_dir(path):
  """Lists contents of requested directory."""
  requested_path = os.path.join(TEST_CASES_PATH, path)
  if not os.path.exists(requested_path):
    return abort(404)

  if os.path.isdir(requested_path):
    files = os.listdir(requested_path)
    return render_template("list-crawler-dir.html", files=files, path=path)

  if os.path.isfile(requested_path):
    return send_from_directory("test-cases/crawler_tests", path)
