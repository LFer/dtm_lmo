from openerp.osv import osv,fields
import datetime

class lmo_employee(osv.osv):
	_inherit="hr.employee"
	_columns={
		'employee':fields.one2many('lmo.account', 'employee_id', 'account'),
		'account_currency_id':fields.many2one('lmo.currency','Account currency'),
	}

lmo_employee()

class lmo_res_company(osv.osv):
	_inherit="res.company"
	_columns={
		'payroll_ids':fields.one2many('lmo.payroll.dictionary','company_id','Liquidations'),
		'overdraft_code':fields.many2one('lmo.payroll.code', 'hr_company_uy','Overdraft credit code'),
		'retent_overdraft_code':fields.many2one('lmo.payroll.code', 'Retention credit code'),
	}

lmo_res_company()

class lmo_payroll_code(osv.osv):
	_description="Code history"
	_name="lmo.payroll.code"
	_columns={
		'pcode_id':fields.integer('Code',size=225,required=True),
		'payroll_id':fields.many2one('lmo.payroll.dictionary','Associated liquidation'),
		'pcode_description':fields.char('Description',size=50),
		'pcode_short_descr':fields.char('Short description', size=15),
		'pcode_credit_or_debit':fields.selection((('H','Credit'),('R','Retention')),'Credit/Retention',required=True),
		'pcode_unit_type':fields.selection((('I','Amount'),('%','Percentage'),('U','Unit'),('T','Days/hours/minutes'),('R','Retroactive')),'Unit',required=True),
		'pcode_autogen':fields.selection((('G','From fixed credits and retentions'),('N','Not generated from credits and retentions')),'Automatic code',required=True),
		'pcode_movement_type':fields.selection((('S','Salary'),('J',"Day's wages"),('C','Common movement')),'Movement Type',required=True),
		'pcode_receipt_type':fields.char('Line type', size=1,required=True),
		'pcode_bases':fields.one2many('lmo.payroll.code.basis','pcode_id','Associated base'),
		'pcode_taxbases':fields.one2many('lmo.payroll.code.taxbase','pcode_id','Associated tax bases'),
		'pcode_taxapplications':fields.one2many('lmo.payroll.code.taxapplication','pcode_id','Associated tax applications')
	}
    	def name_get(self, cr, uid, ids, context=None):
       	    if not ids:
                return []
            reads = self.read(cr, uid, ids, ['payroll_id','pcode_id','pcode_short_descr'], context=context)
            res = []
            for record in reads:
	    	#in case there is no description, don't use it or type error will pop
	    	description = record['pcode_short_descr']
	    	if not description:
			description = 'No descr'

                #res.append((record['id'],u'' + record['payroll_id'][1] + u' - ' + str(record['pcode_id']) + u' - ' + description))
            return res
	_sql_constraints=[('codigo_unico','unique(pcode_id,payroll_id)',"It is not possible to have two codes with the same identifier number on the same liquidation.")]

	pcode_receipt_type = set(map(lambda x: chr(x),range(ord('A'),ord('Z')+1)))-{'C','T','P'}
	def _receipt_type_constraint(self,cr,uid,ids,context=None):
		records = self.browse(cr,uid,ids,context=context)
		for record in records:
			return record['pcode_receipt_type'] in  self.pcode_receipt_type

	_constraints=[(_receipt_type_constraint,'Receipt type must be a capitalized letter distinct from C, T and P',['pcode_receipt_type'])]
lmo_payroll_code()

class payroll_dictionary(osv.osv):
	_description="Liquidation"
	_name="lmo.payroll.dictionary"
    	def name_get(self, cr, uid, ids, context=None):
       	    if not ids:
                return []
            reads = self.read(cr, uid, ids, ['payroll_date','company_id'], context=context)
            res = []
            for record in reads:
                res.append((record['id'],'Liquidation: ' + record['company_id'][1] + ' - ' + record['payroll_date']))
            return res
	_columns={
		'payroll_currency':fields.many2one('lmo.currency', 'Currency'),
		'company_id':fields.many2one('res.company','Associated Company',required=True),
		'payroll_code':fields.one2many('lmo.payroll.code','payroll_id','Associated codes'),
		'payroll_id':fields.integer('Liquidation identifier',size=5,required=True),
		'payroll_date':fields.date('Date',required=True),
		'payroll_description':fields.char('Liquidation description',size=30,required=True),
		'payroll_particular':fields.selection((('T','Total'),('P','Particular')),'Particular Liquidacion',required=True),
		'payroll_group':fields.selection((('T','Total'),('G','Employee group')),'Liquidation by groups',required=True),
		'payroll_code_type':fields.selection((('T','Total'),('C','Code group')),'Liquidation by code',required=True)

	}

	_sql_constraints=[('unique_liquidacion','unique(payroll_id)','The liquidation identifier must be unique!')]

payroll_dictionary()

class code_basis(osv.osv):
	_description="Code basis"
	_name="lmo.payroll.code.basis"
	_columns={
		'pcode_id':fields.many2one('lmo.payroll.code','Associated code'),
		'basis_tariff':fields.float('Tariff',digits=(11,4),required=True),
		'basis_unit_value':fields.float('Unit value',digits=(11,4),required=True),
		'basis_minimum':fields.float('Minimum',digits=(11,4),required=True),
		'basis_exceeds':fields.float('Exceeds',digits=(11,4),required=True),
		'basis_cap':fields.float('Minimum',digits=(11,4),required=True),
		'basis_day':fields.float('Basis day',digits=(11,4),required=True),
		'basis_hour':fields.float('Basis hour',digits=(11,4),required=True),
		'basis_computation_type':fields.selection((('+','Addition'),('-','Substraction'),('*','Multiplication'),('/','Division')),'Computation type',required=True)
	}

code_basis()

class tax_base(osv.osv):
	_description="Taxbase"
	_name="lmo.payroll.code.taxbase"
	_columns={
		'pcode_id':fields.many2one('lmo.payroll.code','associated code'),
		'taxbase_id':fields.integer('Taxbase identifier',size=5,required=True),
		'taxbase_percentage':fields.float('Percentage',digits=(3,2),required=True)
	}

class tax_application(osv.osv):
	_description="Application"
	_name="lmo.payroll.code.taxapplication"
	_columns={
		'pcode_id':fields.many2one('lmo.payroll.code','Tax application identifier'),
		'application_line':fields.integer('Line',size=3,required=True),
		'application_amount_from':fields.float('Amount from',digits=(15,2),required=True),
		'application_amount_upto':fields.float('Amount up to',digits=(15,2),required=True),
		'application_employee_contrib':fields.float('% employee',digits=(15,2),required=True),
		'application_employer_contrib':fields.float('% patron',digits=(15,2),required=True),
		'application_amount_cap':fields.float('Application amount cap',digits=(15,2),required=True),
		'application_progressive':fields.selection((('O','Progressive'),('L','Progressional')),'Progressive/Progressional',required=True)
	}

class lmo_fix(osv.osv):
	_description="Fixed credits and deductions"
	_name= "lmo.fix"
	_columns= {
		'payroll_id':fields.many2one('lmo.payroll.dictionary', 'Liquidation', size=5, required=True),
		'employee_id':fields.many2one('hr.employee', 'Employee', size=10, required=True),
		'section_id':fields.many2one('hr.section','Section', required=True),
		'code_id':fields.many2one('lmo.payroll.code','Code',required=True),
		'aadfixed_place_of_payment':fields.char('Place of payment', required=True),
		'aadfixed_unit':fields.integer('Units',size=5),
		'aadfixed_datetime':fields.datetime('Date and time', required=True),
		'aadfixed_unit_amount':fields.float('Unit amount',digits=(15,2)),
		'aadfixed_total_amount':fields.float('Total amount',digits=(15,2)),
	}

lmo_fix()

class lmo_new(osv.osv):
	_description="Variable credits and deductions"
	_name="lmo.new"
	_columns={
		'payroll_id':fields.many2one('lmo.payroll.dictionary', 'Liquidation', size=5, required=True),
		'employee_id':fields.many2one('hr.employee', 'Employee', size=10, required=True),
		'section_id':fields.many2one('hr.section','Section', required=True),
		'aadnews_place_of_payment':fields.char('Place of payment'),
		'code_id':fields.many2one('lmo.payroll.code','Code', required=True),
		'aadnews_unit':fields.integer('Units',size=5),
		'aadnews_datetime':fields.datetime('Date and time', required=True),
		'aadnews_unit_amount':fields.float('Unit amount',digits=(15,2)),
		'aadnews_total_amount':fields.float('Total amount',digits=(15,2)),
	}

lmo_new()

# give a meaningful definition of rounding code ACA ES DONDE VOY AGREGAR LO QUE ME PIDE LA DOCUMENTACION
class lmo_currency(osv.osv):
	_description="Currency"
	_name="lmo.currency"
    	def name_get(self, cr, uid, ids, context=None):
       	    if not ids:
                return []
            reads = self.read(cr, uid, ids, ['currency_code','currency_name'], context=context)
            res = []
            for record in reads:
                res.append((record['id'],'' + record['currency_code'] + ' - ' + record['currency_name']))
            return res
	_columns= {
		'currency_name':fields.char('Name',required=True),
		'currency_code':fields.char('Currency code',required=True,size=3),
		'currency_related_groups':fields.one2many('lmo.currency.group', 'currency_id','Associated bill groups'),
		'round_liquid_code':fields.many2one('lmo.payroll.code', 'Codigo de redoneo de liquido'),
	}

lmo_currency()

class lmo_currency_group(osv.osv):
	_description="Currency groups"
	_name="lmo.currency.group"
	_columns={
		'currency_id':fields.many2one("lmo.currency","Associated currency"),
		'currency_rounding_pay':fields.float('Credits rounding', digits=(5,2), required=True),
		'currency_rounding_deductions':fields.float('Deductions rounding', digits=(5,2), required=True),
		'currency_date_start':fields.date("Valid from",required=True),
        'currency_date_finish':fields.date("Valid up to", required=True),
		'currency_bills':fields.one2many("lmo.bill","currency_group_id","Associated bills"),
		'currency_current':fields.boolean("Enabled"),
	}


lmo_currency_group()

class lmo_bill(osv.osv):
	_description="Billete"
	_name="lmo.bill"
	_columns={
		'currency_group_id':fields.many2one('lmo.currency.group','Group associated'),
		'bill_id':fields.float('Bill type', digits=(7,2), required=True),
		'bill_description':fields.char('Bill description', required=True),
	}

lmo_bill()



class lmo_account (osv.osv):
	_description="Contabilizacion"
	_name="lmo.account"
	_columns={
		'liquidation_id':fields.many2one('lmo.payroll.dictionary', 'Liquidation', size=5),
		'accounting_records_id':fields.char('Accountig records', size=5),
		'code_id':fields.many2one('lmo.payroll.code', 'Code' , size=5),
		'active_inactive':fields.selection((('A','Active'),('I','Inactive')),'Active/Inactive'),
		'department_id':fields.many2one('hr.department','department'),
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
