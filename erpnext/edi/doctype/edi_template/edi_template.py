# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.model.document import Document
from frappe.modules.utils import export_module_json, get_doc_module
from lxml import etree

from erpnext.edi.doctype.edi_log.edi_log import EDILog

SNIPPETS = dict()

SNIPPETS[("context", "get_context")] = """
import frappe
from erpnext.edi.edi_template.edi_template import EDITemplate

def get_context(self: EDITemplate, doc: "Document") -> None:
	return {"doc": doc}
"""

SNIPPETS[("sign", "sign")] = """
import frappe
from lxml import etree
from signxml import DigestAlgorithm
from signxml.xades import (
	XAdESSignaturePolicy,
	XAdESSigner,
)

from frappe.model import Document

from erpnext.edi.edi_template.edi_template import EDITemplate


SIGNATURE_POLICY = XAdESSignaturePolicy(
	DigestMethod=DigestAlgorithm.SHA256,
	...
)



def sign(self: EDITemplate, render: str, doc: Document) -> str:
	key_file_doc = frappe.get_doc("File", {"file_url": self.keyfile})
	cert_file_doc = frappe.get_doc("File", {"file_url": self.certfile})

	key_file_content = key_file_doc.get_content()
	cert_file_content = cert_file_doc.get_content()

	signer = XAdESSIgner(
		signature_policy=SIGNATURE_POLICY,
		...
	)
	return etree.tostring(
		signer.sign(etree.XML(render)), key=key_file_content, cert=cert_file_content),
		pretty_print=True,
		xml_declaration=True,
	).decode()

"""

SNIPPETS[("validate", "get_validation")] = """
from lxml import etree

import frappe
from frappe import _

from erpnext.edi.edi_template.edi_template import EDITemplate

def get_validation(self: EDITemplate, render: str) -> None:

	class MyExtElement(etree.XSLTExtension):
		def execute(self, context, self_node, input_node, output_parent):
			...

	transform = etree.XSLT(self.validation, extensions={
		("textns", "ext"): MyExtElement(),
	})
	result = transform(etree.XML(render))
	if not True:
		frappe.throw(_("I failed"))
"""

SNIPPETS[("parse", "get_parsed")] = """
from lxml import etree
from lxml import objectify

import frappe
from frappe import _

from erpnext.edi.edi_template.edi_template import EDITemplate

def get_parsed(self: EDITemplate, render: str) -> None:
	schema = None
	if self.schema:
		schema = etree.XMLSchema(self.schema)
	parser = objectify.makeparser(schema=schema)
	try:
		src = objectify.fromstring(render, parser)
	except etree.XMLSytaxError:
		frappe.throw(_("Invalid Schema"))

	doc = frappe.new_doc(self.bound_doctype)
	...
	return doc
"""

SNIPPETS[("submit", "submit")] = """
import xmlsec
import zeep
from lxml import etree
from zeep.cache import Base
from zeep.plugins import HistoryPlugin
from zeep.transports import Transport
from zeep.wsse import utils
from zeep.wsse.signature import BinarySignature


from frappe.model import Document

from erpnext.edi.edi_template.edi_template import EDITemplate


class FrappeCache(Base):
	def __init__(self, timeout=3600):
		self._timeout = timeout

	def add(self, url, content):
		frappe.cache().set_value(
			key=f"edi|{url}",
			val=content,
			expires_in_sec=self._timeout
		)

	def get(self, url):
		if cached_data := frappe.cache().get_value(f"edi|{url}"):
			return cached_data
		return None


def submit(self: EDITemplate, render: str, doc: Document) -> None:
	key_file_doc = frappe.get_doc("File", {"file_url": self.keyfile})
	cert_file_doc = frappe.get_doc("File", {"file_url": self.certfile})

	key_file = key_file_doc.get_full_path()
	cert_file = cert_file_doc.get_full_path()

	history = HistoryPlugin()
	plugins = set(
		...
	)

	client = Client(
		self.submit_url,
		transport=Transport(
			cache=FrappeCache(),
			...
		),
		wsse=BinarySignature(
			key_file=key_file,
			certfile=cert_file,
			signature_method=xmlsec.Transform.RSA_SHA256,
			digest_method=xmlsec.Transform.SHA256,
		),
		plugins=(*plugins, history),
	)

	response = client.service.DoSomething(
		...
	)

	def is_ok(resp):
		...

	def needs_retry(resp):
		...

	def process(history):
		return {
			"request_header": history.last_sent["headers"],
			"request": etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True),
			"response_header": history.last_received["headers"],
			"response": etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True),
		}

	req = etree.tostring(history.last_sent, encoding="unicode", pretty_print=True)
	resp = etree.tostring(history.last_received, encoding="unicode", pretty_print=True)

	if is_ok(repsonse):
		self.write_log(doc, status="Success", **process(history))
		doc.db_set(
			...
		)
		...
	elif needs_retry(response):
		self.write_log(doc, status="Queued", **process(history))
	else:
		self.write_log(doc, status="Error", **process(history))
		doc.log_error("EDI submittion failed", frappe.utils.get_url_to_form(log.doctype, log.docname))
		doc.db_set(
			...
		)
		...
"""


def use_module_if_standard(func):
	def wrapper(self, *args, **kwargs):
		if self.is_standard:
			module_name = "{app}.{module}.{doctype}.{name}".format(
				app=frappe.local.module_app[frappe.scrub(self.module)],
				doctype=frappe.scrub(self.boun_doctype),
				module=frappe.scrub(self.module),
				name=frappe.scrub(self.name),
			)
			module = frappe.get_module(module_name)
			if hasattr(module, func.__name__):
				module_func = getattr(module, func.__name__)
			return module_func(self, *args, **kwargs)
		return func(self, *args, **kwargs)

	return wrapper


class EDITemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.edi.doctype.bound_edi_template_code_lists.bound_edi_template_code_lists import (
			BoundEDITemplateCodeLists,
		)
		from erpnext.edi.doctype.bound_edi_template_common_codes.bound_edi_template_common_codes import (
			BoundEDITemplateCommonCodes,
		)

		bound_code_lists: DF.Table[BoundEDITemplateCodeLists]
		bound_common_codes: DF.Table[BoundEDITemplateCommonCodes]
		bound_doctype: DF.Link
		is_standard: DF.Check
		module: DF.Link | None
		schema: DF.Code | None
		status: DF.Literal["Draft", "Validation", "Production"]
		template: DF.Code | None
		validation: DF.Code | None
	# end: auto-generated types

	@use_module_if_standard
	def get_context(self, doc: Document) -> dict:
		return {"doc": doc}

	@use_module_if_standard
	def get_validation(self, render: str) -> None:
		pass

	@use_module_if_standard
	def sign(self, render: str, doc: Document) -> str:
		return render

	def get_render(self, doc: Document) -> str:
		context = self.get_context(doc)
		render = frappe.render_template(self.template, context)
		signed = self.sign(render, doc)
		self.get_validation(signed)
		return signed

	@use_module_if_standard
	def get_parsed(self, render: str) -> Document | None:
		pass

	@use_module_if_standard
	def submit(self, render: str, doc: Document) -> None:
		pass

	def write_log(
		self,
		doc: Document,
		status: str,
		request_header: str,
		request: str,
		response_header: str,
		response: str,
	) -> EDILog:
		log = frappe.new_doc("EDI Log")
		log.edi = self.name
		log.reference_doctype = doc.doctype
		log.reference_docname = doc.docname
		log.status = status
		log.request_header = request_header
		log.response_header = response_header
		log.request = request
		log.response = response
		return log.save(ignore_permissions=True)

	# field content primes over file content
	def get_code_fields(self):
		return {"template": "xml", "validation": "check.xml", "schema": "schema.xml"}

	def on_update(self):
		path = export_module_json(self, self.is_standard, self.module)
		if not path:
			return
		path = os.path.dirname(path)
		if (init := os.path.join(path, "__init__.py")) and os.path.getsize(init) == 0:
			with open(init, "w") as f:
				for file, function in SNIPPETS.keys():
					f.write(f"from .{file} import {function}\n")

		for (file, _function), content in SNIPPETS.items():
			file_path = os.path.join(path, f"{file}.py")
			if not os.path.exists(file_path):
				with open(file_path, "w") as f:
					f.write(content)
