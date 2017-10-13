# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    procedure_ids = fields.Many2many('procedure.assignment', 'issue_id',
                                     string='Procedures',
                                     domain=[('procedure_id.parent_id', '=', False)],
                                     )

    checklist_ids = fields.Many2many('procedure.assignment', 'issue_id',
                                     string='Checklist',
                                     domain=[('procedure_id.parent_id', '!=', False)],
                                     )
