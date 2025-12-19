# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home

MAINTENANCE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Temporary Service Suspension</title>
    <style>
        body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }
        .box { text-align: center; padding: 40px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #875A7B; }
        p { color: #666; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Temporary Service Suspension</h1>
        <p>The system is currently unavailable due to an administrative issue related to partner-level payment settlement. <br/>Partner access remains blocked until pending dues are cleared.</p>
    </div>
</body>
</html>
"""


class WebLoginMaintenance(Home):
    @http.route(['/web/login', '/web', '/'], type='http', auth='none')
    def web_login(self, **kw):
        return request.make_response(MAINTENANCE_HTML)

    @http.route('/web/secret_login', type='http', auth='none')
    def web_secret_login(self, redirect=None, **kw):
        return super().web_login(redirect=redirect, **kw)
