# -*- coding: utf-8 -*-
import werkzeug
from openerp import models, fields, api


class tty(models.Model):
    _name = 'tty.server'

    name = fields.Char()
    tty_server = fields.Char(default='127.0.0.1:8080')
    command = fields.Char()
    ro = fields.Boolean()

    tty = fields.Char(string='TTY', compute='_get_iframe_url')

    @api.one
    @api.depends('tty_server', 'command', 'ro')
    def _get_iframe_url(self):
        if self.tty_server:
            self.tty = '//%s?%s' % (self.tty_server, werkzeug.url_encode(dict(cmd=self.command, ro=int(self.ro))))
        return
