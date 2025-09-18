import os
token = (data.get("token") or "").strip()
hwid = (data.get("hwid") or "").strip()
if not token or not hwid:
return jsonify({"status":"error","message":"token and hwid required"}), 400


thash = sha256_hex(token)
lic = License.query.filter_by(token_hash=thash).first()
if not lic or not lic.active:
return jsonify({"status":"error","message":"invalid_or_inactive"}), 403


if is_expired(lic):
return jsonify({"status":"error","message":"expired"}), 403


if lic.bound_hwid == hwid:
return jsonify({"status":"ok","message":"valid"})
else:
return jsonify({"status":"error","message":"hwid_mismatch"}), 403


# ------- Admin panel & API --------
@app.route("/admin")
@require_admin
def admin_panel():
licenses = License.query.order_by(License.created_at.desc()).all()
return render_template("admin.html", licenses=licenses)


@app.route("/admin/add", methods=["POST"])
@require_admin
def admin_add():
token = (request.form.get("token") or "").strip()
description = request.form.get("description") or ""
expires_at_str = (request.form.get("expires_at") or "").strip() # expect YYYY-MM-DD or blank
expires_at = None
if expires_at_str:
try:
expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d")
except Exception:
expires_at = None


if not token:
return redirect(url_for("admin_panel"))
thash = sha256_hex(token)
if License.query.filter_by(token_hash=thash).first():
return redirect(url_for("admin_panel"))
lic = License(token_hash=thash, description=description, expires_at=expires_at)
db.session.add(lic)
db.session.commit()
return redirect(url_for("admin_panel"))


@app.route("/admin/delete/<int:id>", methods=["POST"])
@require_admin
def admin_delete(id):
lic = License.query.get(id)
if lic:
db.session.delete(lic)
db.session.commit()
return redirect(url_for("admin_panel"))


@app.route("/admin/unbind/<int:id>", methods=["POST"])
@require_admin
def admin_unbind(id):
lic = License.query.get(id)
if lic:
lic.bound_hwid = None
lic.used = False
db.session.commit()
return redirect(url_for("admin_panel"))


if __name__ == "__main__":
port = int(os.getenv("PORT", 5000))
app.run(host="0.0.0.0", port=port)
