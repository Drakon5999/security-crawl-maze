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
import hashlib
from flask import request

crawler_tests = Blueprint(
    "crawler_tests", __name__, template_folder="templates")

# Global app.instance_path is not accessible from blueprints ¯\_(ツ)_/¯.
TEST_CASES_PATH = os.path.abspath(__file__ + "/../../../test-cases/crawler_tests/")


def try_get_int(s, default=1):
    try:
        res = int(s)
    except Exception as e:
        res = default
    return res


@crawler_tests.route("/infinity_app/in_param/")
def in_param_index():
    path = try_get_int(request.args.get('path'))
    return render_template("infinity_site.html", path=path,
                           next_url="in_param?path={}".format(path + 1),
                           prev_url="in_param?path={}".format(path - 1),
                           interesting_url="in_param/interesting_url.found",
                           )


@crawler_tests.route("/infinity_app/in_path/")
@crawler_tests.route("/infinity_app/in_path/<string:path>")
def in_path_index(path):
    path = try_get_int(path)

    return render_template("infinity_site.html", path=path,
                           next_url="in_path/{}".format(path + 1),
                           prev_url="in_path/{}".format(path - 1),
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


@crawler_tests.route("/statefull/cyclic/")
@crawler_tests.route("/statefull/cyclic/<string:md5>.found")
def cyclic(md5=None):
    foo = 0
    mod = 5
    if not request.cookies.get('foo') or not md5:
        foo = 1
        one_hash = hashlib.md5(b"1").hexdigest()
        if not md5 or md5 == one_hash:
            md5 = one_hash
        else:
            return make_response("not found", 404)
    else:
        foo = try_get_int(request.cookies.get('foo'))
    foo_hash = hashlib.md5(str(foo).encode('utf-8')).hexdigest()
    foo_next_hash = hashlib.md5(str((foo+1) % mod).encode('utf-8')).hexdigest()
    if foo_hash == md5 and foo < mod:
        resp = make_response(render_template("cyclic.html", path=foo_hash, next_url="/cyclic/{}.found".format(foo_next_hash)), 200)
        resp.set_cookie('foo', str(foo), max_age=60*60*24*365*2)
        return resp
    elif foo_next_hash == md5:
        resp = make_response(render_template("cyclic.html", path=foo_next_hash, next_url="/cyclic/{}.found".format(hashlib.md5(str((foo+2) % mod).encode('utf-8')).hexdigest())), 200)
        resp.set_cookie('foo', str((foo+1)%mod), max_age=60*60*24*365*2)
        return resp
    else:
        return make_response("not found", 404)


@crawler_tests.route("/statefull/proxy/")
def proxy_first():
    foo = 0
    mod = 5
    if not request.cookies.get('foo_proxy'):
        foo = 1
    else:
        foo = (try_get_int(request.cookies.get('foo_proxy'), 0) + 1) % mod
    resp = make_response(render_template("proxy.html", next_url="proxy/internal", header="Proxy", link_text="Try to explore!", home_url="proxy/"), 200)
    resp.set_cookie('foo_proxy', str(foo), max_age=60*60*24*365*2)
    return resp


@crawler_tests.route("/statefull/proxy/internal")
def proxy_internal():
    foo = try_get_int(request.cookies.get('foo_proxy'))
    hexdigest = hashlib.md5(str(foo).encode('utf-8')).hexdigest()
    resp = make_response(render_template("proxy.html", next_url="proxy/internal/{}.found".format(hexdigest), header=hexdigest, link_text="Found link", home_url="proxy/"), 200)
    resp.set_cookie('foo', str(foo), max_age=60*60*24*365*2)
    return resp


@crawler_tests.route("/statefull/proxy/internal/<string:md5>.found")
def proxy_found(md5):
    foo = try_get_int(request.cookies.get('foo_proxy'))
    hexdigest = hashlib.md5(str(foo).encode('utf-8')).hexdigest()
    if md5 == hexdigest:
        return make_response("passed", 200)
    else:
        return make_response("not found", 404)


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
