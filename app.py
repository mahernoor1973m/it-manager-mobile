from datetime import datetime
import os
import pandas as pd
import streamlit as st

# إعدادات صفحة الويب لتكون متجاوبة (Wide layout مناسب للشاشات والمرونة)
st.set_page_config(
    page_title="IT Manager Pro Mobile", page_icon="📱", layout="wide"
)

# --- تنسيقات CSS إضافية لتحسين العرض على شاشات الهواتف المحمولة ---
st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        h1 { font-size: 22px !important; }
        h2 { font-size: 18px !important; }
        h3 { font-size: 16px !important; }
        .stButton button { width: 100%; font-size: 14px !important; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- قاعدة بيانات المستخدمين والصلاحيات ---
if "users_db" not in st.session_state:
  st.session_state["users_db"] = {
      "admin": {"password": "12345", "role": "مدير النظام (Admin)"},
      "طارق": {"password": "12345", "role": "مستخدم عادي (فني)"},
  }

# --- إدارة حالة تسجيل الدخول ---
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "username" not in st.session_state:
  st.session_state["username"] = ""
if "user_role" not in st.session_state:
  st.session_state["user_role"] = ""

# --- شاشة تسجيل الدخول إذا لم يتم تسجيل الدخول بعد ---
if not st.session_state["logged_in"]:
  st.title("📱 تسجيل الدخول - IT Manager Pro")
  st.info(
      "أهلاً بك! يمكنك إدخال بيانات حسابك، أو الضغط مباشرة على 'دخول' بدون كتابة"
      " شيء لاستعراض النظام كمستعرض فقط."
  )

  with st.form("login_form"):
    input_user = st.text_input("اسم المستخدم")
    input_pass = st.text_input("كلمة المرور", type="password")
    login_btn = st.form_submit_button("دخول للموبايل 🚀")

    if login_btn:
      if input_user.strip() == "" and input_pass.strip() == "":
        st.session_state["logged_in"] = True
        st.session_state["username"] = "مستعرض (موبايل)"
        st.session_state["user_role"] = "مستعرض فقط (Viewer)"
        st.success("تم الدخول كمستعرض بنجاح!")
        st.rerun()
      else:
        users = st.session_state["users_db"]
        if (
            input_user in users
            and users[input_user]["password"] == input_pass
        ):
          st.session_state["logged_in"] = True
          st.session_state["username"] = input_user
          st.session_state["user_role"] = users[input_user]["role"]
          st.success("تم تسجيل الدخول بنجاح!")
          st.rerun()
        else:
          st.error(
              "خطأ في البيانات! (اترك الحقول فارغة للدخول كـ مستعرض فقط)"
          )

  st.stop()

# ==========================================
# --- الكود الرئيسي للبرنامج (وضع الموبايل) ---
# ==========================================

st.sidebar.title("📱 IT Manager Mobile")
st.sidebar.markdown(
    f"👤 **المستخدم:** {st.session_state['username']} \n\n🛡️"
    f" **الصلاحية:** {st.session_state['user_role']}"
)

if st.sidebar.button("🚪 تسجيل الخروج"):
  st.session_state["logged_in"] = False
  st.session_state["username"] = ""
  st.session_state["user_role"] = ""
  st.rerun()

st.sidebar.markdown("---")

section = st.sidebar.selectbox(
    "القائمة الرئيسية",
    [
        "لوحة المؤشرات (Dashboard)",
        "إدارة الأجهزة والبيانات",
        "🛠️ سجلات الصيانة",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("📁 حالة الملفات التلقائية")
st.sidebar.info(
    "🔄 يتم جلب بيانات الأجهزة تلقائياً من ملف (devices.xlsx) على السحابة."
)

# --- قراءة ملف الإكسل تلقائياً من مجلد المشروع (بدون رفع يدوي) ---
excel_file_path = "devices.xlsx"

if os.path.exists(excel_file_path):
  try:
    df_loaded = pd.read_excel(excel_file_path)
    df_loaded = df_loaded.astype(str)
    df_loaded.replace("nan", "", inplace=True)
    st.session_state["device_data"] = df_loaded
  except Exception as e:
    st.sidebar.error(f"خطأ في قراءة ملف الإكسل التلقائي: {e}")
else:
  st.session_state["device_data"] = None

# استرجاع سجلات الصيانة والأنواع من النسخ الاحتياطية السحابية
if "maint_records" not in st.session_state:
  if os.path.exists("saved_maintenance_backup.csv"):
    try:
      df_maint_saved = pd.read_csv(
          "saved_maintenance_backup.csv", dtype={"التكلفة ($)": float}
      )
      df_maint_saved.fillna("", inplace=True)
      st.session_state["maint_records"] = df_maint_saved.to_dict(
          orient="records"
      )
    except:
      st.session_state["maint_records"] = []
  else:
    st.session_state["maint_records"] = []

if "maintenance_types" not in st.session_state:
  if os.path.exists("saved_maint_types.csv"):
    try:
      df_types = pd.read_csv("saved_maint_types.csv", dtype=str)
      st.session_state["maintenance_types"] = df_types[
          "maintenance_type"
      ].tolist()
    except:
      st.session_state["maintenance_types"] = [
          "صيانة دورية",
          "إصلاح هاردوير",
          "فرمتة وترتيب نظام",
          "استبدال قطعة",
          "مشكلة شبكة",
      ]
  else:
    st.session_state["maintenance_types"] = [
        "صيانة دورية",
        "إصلاح هاردوير",
        "فرمتة وترتيب نظام",
        "استبدال قطعة",
        "مشكلة شبكة",
    ]


def save_maintenance_to_disk():
  if st.session_state["maint_records"]:
    df_m = pd.DataFrame(st.session_state["maint_records"])
    df_m.to_csv("saved_maintenance_backup.csv", index=False)
  else:
    if os.path.exists("saved_maintenance_backup.csv"):
      os.remove("saved_maintenance_backup.csv")


def save_maint_types_to_disk():
  df_t = pd.DataFrame(
      {"maintenance_type": st.session_state["maintenance_types"]}
  )
  df_t.to_csv("saved_maint_types.csv", index=False)


# زر تصفير سجلات الصيانة (خاص بالمدير)
if st.session_state["user_role"] == "مدير النظام (Admin)":
  st.sidebar.markdown("---")
  if st.sidebar.button("🗑️ تصفير سجلات الصيانة"):
    if "maint_records" in st.session_state:
      st.session_state["maint_records"] = []
    if os.path.exists("saved_maintenance_backup.csv"):
      os.remove("saved_maintenance_backup.csv")
    st.sidebar.success("تم تصفير سجلات الصيانة بنجاح!")
    st.rerun()

# --- محتوى الصفحات ---

if section == "لوحة المؤشرات (Dashboard)":
  st.title("📊 لوحة المؤشرات والإحصاءات")

  if (
      "device_data" in st.session_state
      and st.session_state["device_data"] is not None
  ):
    df = st.session_state["device_data"]
    total_devices = len(df)

    dept_col = None
    for col in df.columns:
      if "قسم" in str(col) or "dept" in str(col).lower():
        dept_col = col
        break

    active_departments = (
        df[dept_col].nunique() if dept_col else len(df.columns)
    )
    total_maintenance = (
        len(st.session_state["maint_records"])
        if "maint_records" in st.session_state
        else 0
    )
    total_cost = 0.0

    if "maint_records" in st.session_state and st.session_state["maint_records"]:
      total_cost = sum(
          float(item.get("التكلفة ($)", 0.0))
          for item in st.session_state["maint_records"]
          if str(item.get("التكلفة ($)", 0.0)).strip() != ""
      )

    col1, col2 = st.columns(2)
    with col1:
      st.metric(label="إجمالي الأجهزة", value=total_devices)
      st.metric(label="إجمالي المصاريف", value=f"${total_cost:,.2f}")
    with col2:
      st.metric(label="مهام الصيانة", value=total_maintenance)
      st.metric(label="الأقسام النشطة", value=active_departments)

    st.markdown("---")
    st.subheader("📈 توزيع الأجهزة")
    if dept_col:
      dept_counts = df[dept_col].value_counts()
      st.bar_chart(dept_counts)
    else:
      st.info("عمود القسم غير متوفر للرسم البياني.")

    st.markdown("---")
    st.subheader("📋 الجدول العام:")
    st.dataframe(df, use_container_width=True)
  else:
    st.warning(
        "⚠️ لم يتم العثور على ملف (devices.xlsx) في مجلد المشروع على السحابة."
    )

elif section == "إدارة الأجهزة والبيانات":
  st.title("💻 استعراض الأجهزة والبيانات")

  if (
      "device_data" in st.session_state
      and st.session_state["device_data"] is not None
  ):
    df = st.session_state["device_data"]
    st.info(
        "👁️ البيانات مستوردة تلقائياً من ملف الإكسل الأساسي. لتعديلها، قم"
        " بتحديث ملف الإكسل على جهازك ورفعه إلى جيت هب."
    )
    st.dataframe(df, use_container_width=True)
  else:
    st.info("الرجاء إضافة ملف الأجهزة (devices.xlsx) إلى مجلد المشروع أولاً.")

elif section == "🛠️ سجلات الصيانة":
  st.title("🛠️ سجلات الصيانة")

  if st.session_state["maint_records"]:
    df_maint = pd.DataFrame(st.session_state["maint_records"])
    if st.session_state["user_role"] == "مستعرض فقط (Viewer)":
      st.dataframe(df_maint, use_container_width=True)
    else:
      event = st.dataframe(
          df_maint,
          use_container_width=True,
          selection_mode="single-row",
          on_select="rerun",
          key="mobile_maint_table",
      )
      selected_rows = event.selection.get("rows", [])

      if selected_rows:
        sel_idx = selected_rows[0]
        rec = st.session_state["maint_records"][sel_idx]
        with st.form("maint_edit_mob"):
          ed_date = st.text_input("التاريخ", value=str(rec["تاريخ الصيانة"]))
          ed_act = st.text_input("الإجراء", value=str(rec["الإجراء"]))
          ed_cost = st.number_input(
              "التكلفة", value=float(rec.get("التكلفة ($)", 0.0))
          )
          ed_tech = st.text_input("الفني", value=str(rec["الفني"]))

          if st.form_submit_button("حفظ التعديل"):
            st.session_state["maint_records"][sel_idx].update({
                "تاريخ الصيانة": ed_date,
                "الإجراء": ed_act,
                "التكلفة ($)": ed_cost,
                "الفني": ed_tech,
            })
            save_maintenance_to_disk()
            st.success("تم التحديث!")
            st.rerun()
  else:
    st.write("لا توجد سجلات صيانة بعد.")

  if st.session_state["user_role"] != "مستعرض فقط (Viewer)":
    st.markdown("---")
    with st.expander("➕ إضافة صيانة جديدة"):
      with st.form("mob_new_maint"):
        m_date = st.date_input("التاريخ", value=datetime.now())
        issue = st.selectbox(
            "المشكلة", options=st.session_state["maintenance_types"]
        )
        action = st.text_input("الإجراء المتخذ")
        cost = st.number_input("التكلفة ($)", min_value=0.0, step=5.0)
        tech = st.text_input("الفني")

        if st.form_submit_button("حفظ السجل الجديد"):
          st.session_state["maint_records"].append({
              "تاريخ الصيانة": str(m_date),
              "المشكلة": issue,
              "الإجراء": action,
              "التكلفة ($)": cost,
              "الفني": tech,
          })
          save_maintenance_to_disk()
          st.success("تم الإضافة بنجاح! 🎉")
          st.rerun()