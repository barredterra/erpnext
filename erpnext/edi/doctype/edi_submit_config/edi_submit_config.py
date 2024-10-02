# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EDISubmitConfig(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		certfile: DF.Attach | None
		keyfile: DF.Attach | None
		password: DF.Password | None
		submit_url: DF.Data | None
	# end: auto-generated types

	pass
