# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

from openerp.osv import osv,fields
import datetime

class lmo_employee(osv.osv):
    _inherit="hr.employee"
    _columns={
        'employee':fields.one2many('lmo.account', 'employee_id', 'Account'),
        'account_currency_id':fields.many2one('res.currency','Account currency'),
    }

lmo_employee()

class lmo_res_company(osv.osv):
    _inherit="res.company"
    _columns={
        'payroll_ids':fields.one2many('lmo.payroll.dictionary','company_id','Liquidations'),
        'overdraft_code':fields.many2one('lmo.payroll.code', 'hr_company_uy','Overdraft credit code'),
        'retent_overdraft_code':fields.many2one('lmo.payroll.code', 'Retention credit code'),
        'rounding_retent':fields.float('Redondeo por movimiento haber', digits=(11,4)),
        'rounding_have':fields.float('Redondeo por movimiento retencion', digits=(11,4)),
        'total_rounding':fields.float('Redondeo total', digits=(11,4)),
        'min_liq':fields.float('Líquido mínimo', digits=(11,4)),
        'overdraft_type':fields.selection((('N', 'Acepta liquídos negativos'), ('G', 'Genera vale')),'Tipo de tratamiento del sobregiro'),
        'having_code':fields.many2one('lmo.payroll.code','Código de redondeo haber'),
        'retent_code':fields.many2one('lmo.payroll.code','Código de redondeo retención'),
        'code_gen':fields.many2one('lmo.payroll.code','Código del vale Haber a generar'),
        'code_retent':fields.many2one('lmo.payroll.code','Código del vale Retención a transferir'),
    
    }
    

lmo_res_company()

class lmo_payroll_code(osv.osv):
    _description="Code history"
    _name="lmo.payroll.code"
    _columns={
        'pcode_id':fields.integer('Code',size=225,required=True),
        'payroll_id':fields.many2one('lmo.payroll.dictionary','Associated liquidation'),
        'name':fields.char('Description',size=50),
        'pcode_short_descr':fields.char('Short desc.', size=15),
        'pcode_credit_or_debit':fields.selection((('H','Credit'),('R','Retention')),'Credit/Retention',required=True),
        'pcode_unit_type':fields.selection((('I','Amount'),('%','Percentage'),('U','Unit'),('T','Days/Hours/Minutes'),('R','Retroactive')),'Unit',required=True),
        'pcode_autogen':fields.selection((('G','From fixed credits and retentions'),('N','Not generated from credits and retentions')),'Automatic code',required=True),
        'pcode_movement_type':fields.selection((('S','Salary'),('J',"Day's wages"),('C','Common movement')),'Movement type',required=True),
        'pcode_bases':fields.one2many('lmo.payroll.code.basis','pcode_id','Associated base'),
        'pcode_taxbases_ids':fields.one2many('lmo.payroll.code.taxbase','pcode_id','Associated tax bases'),
        'pcode_taxapplications_ids':fields.one2many('lmo.payroll.code.taxapplication','pcode_id','Associated tax applications'),
        'forced_code':fields.boolean('Forced code', required=True),

    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['pcode_id','name'], context=context)
        res = []
        for record in reads:
            res.append((record['id'],str(record['pcode_id']) + u' - ' + record['name']))
        return res

    _sql_constraints=[('unique_code','unique(pcode_id,payroll_id)',"It is not possible to have two codes with the same identifier number on the same liquidation.")]

lmo_payroll_code()

class payroll_dictionary(osv.osv):
    _description="Liquidation"
    _name="lmo.payroll.dictionary"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['payroll_description','payroll_date','company_id'], context=context)
        res = []
        for record in reads:
            res.append((record['id'], record['payroll_description'] + ' - ' + record['company_id'][1] + ' - ' + record['payroll_date']))
        return res

    _columns={
        'payroll_currency':fields.many2one('res.currency', 'Currency', required=True),
        'company_id':fields.many2one('res.company','Associated company',required=True),
        'payroll_code_ids':fields.one2many('lmo.payroll.code','payroll_id','Associated codes'),
        'payroll_date':fields.date('Date',required=True),
        'payroll_description':fields.char('Liquidation desc.',size=30,required=True),
        'payroll_particular':fields.selection((('T','Total'),('P','Particular')),'Particular liquidation',required=True),
        'payroll_group':fields.selection((('T','Total'),('G','Employee group')),'Liquidation by groups',required=True),
        'payroll_code_type':fields.selection((('T','Total'),('C','Code group')),'Liquidation by code',required=True)

    }
    _defaults = {
		'payroll_currency':47,
        }

payroll_dictionary()

class code_basis(osv.osv):
    _description="Code basis"
    _name="lmo.payroll.code.basis"
    _columns={
        'pcode_id':fields.many2one('lmo.payroll.code','Associated code'),
        'basis_tariff':fields.float('Tariff',digits=(11,4)),
        'basis_unit_value':fields.float('Unit value',digits=(11,4)),
        'basis_minimum':fields.float('Minimum',digits=(11,4)),
        'basis_exceeds':fields.float('Exceeds',digits=(11,4)),
        'basis_cap':fields.float('Cap',digits=(11,4)),
        'basis_day':fields.float('Basis day',digits=(11,4)),
        'basis_hour':fields.float('Basis hour',digits=(11,4)),
        'basis_computation_type':fields.selection((('+','Addition'),('-','Substraction'),('*','Multiplication'),('/','Division')),'Computation type'),
    }

code_basis()

class lmo_payroll_code_taxbase(osv.osv):
    _description="Taxbase"
    _name="lmo.payroll.code.taxbase"
    _columns={
        #'pcode_id':fields.many2one('lmo.payroll.code','Associated code'),
        'pcode_id':fields.integer('Original code'),
        'taxbase_id':fields.many2one('lmo.payroll.code','Associated code'),
        'taxbase_percentage':fields.float('Percentage',digits=(3,2),required=True)
    }

    _defaults = {
		'taxbase_percentage': 100,
    }

lmo_payroll_code_taxbase()

class tax_application(osv.osv):
    _description="Application"
    _name="lmo.payroll.code.taxapplication"
    _columns={
        'pcode_id':fields.many2one('lmo.payroll.code','Tax application identifier'),
        'application_line':fields.integer('Line',size=3,required=True),
        'application_amount_from':fields.float('Amount from',digits=(15,2),required=True),
        'application_amount_upto':fields.float('Amount up to',digits=(15,2),required=True),
        'application_employee_contrib':fields.float('% employee',digits=(15,4),required=True),
        'application_employer_contrib':fields.float('% employer',digits=(15,4),required=True),
        'application_amount_cap':fields.float('Application amount cap',digits=(15,2),required=True),
        'application_progressive':fields.selection((('O','Progressive'),('L','Progressional')),'Progressive/Progressional',required=True)
    }

tax_application()

class lmo_credits_and_deductions_fixed(osv.osv):
    _description="Fixed credits and deductions"
    _name= "lmo.credits.and.deductions.fixed"
    _columns= {
        'payroll_id':fields.many2one('lmo.payroll.dictionary', 'Liquidation', size=5, required=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', size=10, required=True),
        'code_id':fields.many2one('lmo.payroll.code','Code',required=True),
        'unit':fields.integer('Units',size=5),
        'day':fields.float('Days'),
        'hour':fields.float('Hours'),
        'minit':fields.integer('Minutes',),
        'unit_amount':fields.float('Unit amount',digits=(15,2)),
        'total_amount':fields.float('Total amount',digits=(15,2)),
        'category':fields.char('Job name'),
        'department_id':fields.many2one('hr.department', 'Department'),
        'pay_type':fields.char('Type of work', size=1),
        'company_id':fields.integer('Company'),
        'currency_id':fields.many2one('res.currency', 'Currency'),
    }
    
    def create(self, cr, uid, values, context=None):
        #departamento
        employee_data = self.pool.get('hr.employee').read(cr, uid, values['employee_id'])
        #compania
        resource_data = self.pool.get('resource.resource').read(cr, uid, employee_data['resource_id'][0])
        #moneda
        currency_data = self.pool.get('lmo.payroll.dictionary').read(cr, uid, values['payroll_id'])
        
        values['department_id'] = employee_data['department_id'][0]
        values['pay_type'] = employee_data['pay_type']
        values['company_id'] = resource_data['company_id'][0]
        values['currency_id'] = currency_data['payroll_currency'][0]
        return super(lmo_credits_and_deductions_fixed, self).create(cr, uid, values, context=context)
        
    def write(self, cr, uid, ids, values, context=None):
        if  'employee_id' in values.keys():
            employee_data = self.pool.get('hr.employee').read(cr, uid, values['employee_id'])
            values['department_id'] = employee_data['department_id'][0]
            values['pay_type'] = employee_data['pay_type'][0]
            values['company_id'] = resource_data['company_id'][0]
            values['currency_id'] = currency_data['payroll_currency'][0]
        return super(lmo_credits_and_deductions_fixed, self).write(cr, uid, ids, values, context=context)
   
lmo_credits_and_deductions_fixed()

class lmo_credits_and_deductions_news(osv.osv):
    _description="Variable credits and deductions"
    _name="lmo.credits.and.deductions.news"
    _columns={
        'payroll_id':fields.many2one('lmo.payroll.dictionary', 'Liquidation', size=5, required=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', size=10, required=True),
        'code_id':fields.many2one('lmo.payroll.code','Code', required=True),
        'unit':fields.integer('Units',size=5),
        'day':fields.float('Days'),
        'hour':fields.float('Hours'),
        'minit':fields.integer('Minutes'),
        'unit_amount':fields.float('Unit amount',digits=(15,2)),
        'total_amount':fields.float('Total amount',digits=(15,2)),
        'category':fields.char('Job name'),
        'department_id':fields.many2one('hr.department', 'Department'),
        'pay_type':fields.char('Type of work', size=1),
        'company_id':fields.integer('Company'),
        'currency_id':fields.many2one('res.currency', 'Currency'),
        
    }
    def create(self, cr, uid, values, context=None):
        #departamento
        employee_data = self.pool.get('hr.employee').read(cr, uid, values['employee_id'])
        #compania
        resource_data = self.pool.get('resource.resource').read(cr, uid, employee_data['resource_id'][0])
        #moneda
        currency_data = self.pool.get('lmo.payroll.dictionary').read(cr, uid, values['payroll_id'])
        
        values['department_id'] = employee_data['department_id'][0]
        values['pay_type'] = employee_data['pay_type']
        values['company_id'] = resource_data['company_id'][0]
        values['currency_id'] = currency_data['payroll_currency'][0]
        return super(lmo_credits_and_deductions_news, self).create(cr, uid, values, context=context)
        
    def write(self, cr, uid, ids, values, context=None):
        if  'employee_id' in values.keys():
            employee_data = self.pool.get('hr.employee').read(cr, uid, values['employee_id'])
            values['department_id'] = employee_data['department_id'][0]
            values['pay_type'] = employee_data['pay_type'][0]
            values['company_id'] = resource_data['company_id'][0]
            values['currency_id'] = currency_data['payroll_currency'][0]
        return super(lmo_credits_and_deductions_news, self).write(cr, uid, ids, values, context=context)

lmo_credits_and_deductions_news()

class lmo_credits_and_deductions_liq(osv.osv):
    _description="Calculated credits and deductions"
    _name="lmo.credits.and.deductions.liq"
    _columns={
        'payroll_id':fields.many2one('lmo.payroll.dictionary', 'Liquidation', size=5, required=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', size=10, required=True),
        'code_id':fields.many2one('lmo.payroll.code', 'Code', required=True),
        'unit':fields.integer('Units', size=5),
        'day':fields.float('Days'),
        'hour':fields.integer('Minutes'),
        'minit':fields.integer('Minutes'),
        'unit_amount':fields.float('Unit amount', digits=(15,2)),
        'total_amount':fields.float('Total amount', digits=(15,2)),
        'employee_contrib':fields.float('Personal taxes', digits=(15,2)),
        'employer_contrib':fields.float('Employer taxes', digits=(15,2)),
        'category':fields.char('Job name'),
        'department_id':fields.many2one('hr.department', 'Department'),
        'pay_type':fields.char('Type of work', size=1),
        'company_id':fields.integer('Company'),
        'currency_id':fields.many2one('res.currency', 'Currency'),
    }

lmo_credits_and_deductions_liq()

class lmo_account (osv.osv):
    _description="Account"
    _name="lmo.account"
    _columns={
        'liquidation_id':fields.many2one('lmo.payroll.dictionary', 'Liquidation', size=5),
        'accounting_records_id':fields.char('Accountig records', size=5),
        'code_id':fields.many2one('lmo.payroll.code', 'Code' , size=5),
        'active_inactive':fields.selection((('A','Active'),('I','Inactive')),'Active/Inactive'),
        'department_id':fields.many2one('hr.department','Department'),
        'section_id':fields.many2one('hr.section','Section',size=5),
        'local_id':fields.many2one('hr.locals', 'Local', size=5),
        'mtss_id':fields.integer('Mtss', size=2),
        'mj_id':fields.selection((('M','Monthly'),('D','Daylaboreer'),('0','All')),'MJ'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'account_planning':fields.char('Accountig plan', size=15),
        'concept_id':fields.char('Concept',size=50),
        'percentage_id':fields.integer('Percentaje', size=5),
        'credit_debit':fields.selection((('D', 'Debt'),('C','Credit')),'Debt/Credit'),
    }

lmo_account()

class res_currency(osv.osv):
    _inherit = 'res.currency'
    _columns = {
        'currency_code':fields.integer('Local currency code',size=3)
    }

res_currency()

