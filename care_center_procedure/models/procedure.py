# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProcedureProcedure(models.Model):
    _name = 'procedure.procedure'
    _order = 'sequence asc'

    @api.multi
    def _get_sequence(self):
        """Calculate default sequence of child procedures"""
        for record in self:
            if not record.parent_id:
                continue
            # don't override sequence
            if record.sequence:
                continue

            print('child ids are', record.child_ids, len(record.child_ids))

            return len(record.child_ids) + 1


    name = fields.Char(required=True)
    description = fields.Html(string='Description')

    parent_id = fields.Many2one('procedure.procedure', string='Procedure', ondelete='cascade',
                                domain=[('parent_id', '=', False)],)
    child_ids = fields.One2many('procedure.procedure', 'parent_id', string='Checklist')
    sequence = fields.Integer('Sequence', default=_get_sequence)

    @api.multi
    def add_checklist(self):
        """Display modal form to add new checklists"""

        form = self.env.ref('care_center_procedure.view_procedure_form')

        return {
            'name': 'Add Checklist',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'procedure.procedure',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'parent_id': self.id, 'default_parent_id': self.id, 'hide_checklist': True},
            'views': [
                (form.id, 'form'),
            ],
        }


class ProcedureAssignment(models.Model):
    _name = "procedure.assignment"
    _inherit = ['ir.needaction_mixin']

    state = fields.Selection([
        ('done', 'Done'),
        ('todo', 'To Do'),
        ('waiting', 'Waiting'),
        ('cancelled', 'Cancelled'),
    ],
     'Status', required=True, copy=False, default='todo')

    name = fields.Char(related='procedure_id.name', store=True)
    procedure_id = fields.Many2one('procedure.procedure', required=True)
    user_id = fields.Many2one('res.users', 'Assigned to', required=True)
    issue_id = fields.Many2one('project.issue', 'Issue', ondelete='cascade', required=False, index="1")
    task_id = fields.Many2one('project.task', 'Task', ondelete='cascade', required=False, index="1")
    hide_button = fields.Boolean(compute='_compute_hide_button')
    recolor = fields.Boolean(compute='_compute_recolor')

    @api.multi
    def _compute_user(self):
        for record in self:
            if self.env.user != record.user_id and self.env.user != record.create_uid:
                record.default_user = record.user_id
            else:
                if self.env.user != record.user_id:
                    record.default_user = record.user_id
                elif self.env.user != record.create_uid:
                    record.default_user = record.create_uid
                elif self.env.user == record.create_uid and self.env.user == record.user_id:
                    record.default_user = self.env.user

    @api.multi
    def _compute_recolor(self):
        for record in self:
            if self.env.user == record.user_id and record.state == 'todo':
                record.recolor = True

    @api.multi
    def _compute_hide_button(self):
        for record in self:
            if self.env.user != record.user_id:
                record.hide_button = True

    @api.model
    def _needaction_domain_get(self):
        if self._needaction:
            return [('state', '=', 'todo'), ('user_id', '=', self.env.uid)]
        return []

    @api.multi
    def change_state_done(self):
        for record in self:
            record.state = 'done'

    @api.multi
    def change_state_todo(self):
        for record in self:
            record.state = 'todo'

    @api.multi
    def change_state_cancelled(self):
        for record in self:
            record.state = 'cancelled'

    @api.multi
    def change_state_waiting(self):
        for record in self:
            record.state = 'waiting'

