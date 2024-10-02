# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EDILog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		edi: DF.Link | None
		reference_docname: DF.DynamicLink | None
		reference_doctype: DF.Link | None
		request: DF.Code | None
		request_header: DF.Code | None
		response: DF.Code | None
		response_header: DF.Code | None
		status: DF.Literal["Queued", "Success", "Error"]
	# end: auto-generated types

	pass
