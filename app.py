from datetime import datetime
import os
import pandas as pd
import streamlit as st

# إعدادات صفحة الويب
st.set_page_config(
    page_title="IT Manager Pro", page_icon="⚡", layout="wide"
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
  st.title("🔐 تسجيل الدخول - IT Manager Pro")
  st.info(
      "الرجاء إدخال اسم المستخدم وكلمة المرور، أو ترك الحقول فارغة والضغط على"
      " 'دخول' للدخول بصيغة (مستعرض فقط)."
  )

  with st.form("login_form"):
    input_user = st.text_input("اسم المستخدم")
    input_pass = st.text_input("كلمة المرور", type="password")
    login_btn = st.form_submit_button("دخول")

    if login_btn:
      # إذا ترك الحقول فارغة تماماً -> دخول كمستعرض فقط
      if input_user.strip() == "" and input_pass.strip() == "":
        st.session_state["logged_in"] = True
        st.session_state["username"] = "زائر (مستعرض)"
        st.session_state["user_role"] = "مستعرض فقط (Viewer)"
        st.success("تم الدخول كمستعرض فقط بنجاح!")
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
              "اسم المستخدم أو كلمة المرور غير صحيحة! (أو اتركها فارغة لدخول"
              " المستعرض)"
          )

  # إيقاف تنفيذ باقي الكود حتى يتم تسجيل الدخول
  st.stop()

# ==========================================
# --- الكود الرئيسي للبرنامج (بعد تسجيل الدخول) ---
# ==========================================

# عرض معلومات المستخدم الحالي في الشريط الجانبي
st.sidebar.title("⚡ IT Manager Pro")
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
    "اختر القسم",
    [
        "لوحة المؤشرات (Dashboard)",
        "إدارة الأجهزة والبيانات",
        "🛠️ سجلات الصيانة",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("📁 إدارة الملفات والأقسام")

# زر الاستعراض ورفع ملف الإكسل (ممنوع على المستعرض فقط)
if st.session_state["user_role"] != "مستعرض فقط (Viewer)":
  uploaded_file = st.sidebar.file_uploader(
      "رفع ملف إكسل (الأجهزة)", type=["xlsx", "xls"]
  )

  if uploaded_file is not None:
    try:
      df = pd.read_excel(uploaded_file)
      df = df.astype(str)
      df.replace("nan", "", inplace=True)
      st.session_state["device_data"] = df
      df.to_csv("saved_devices_backup.csv", index=False)
      st.sidebar.success("تم رفع ملف الأجهزة بنجاح!")
    except Exception as e:
      st.sidebar.error(f"خطأ في قراءة الملف: {e}")
else:
  st.sidebar.info("👁️ حسابك (مستعرض فقط) - ميزة رفع الملفات معطلة.")

# استرجاع بيانات الأجهزة من النسخة الاحتياطية
if (
    "device_data" not in st.session_state
    or st.session_state["device_data"] is None
):
  try:
    if os.path.exists("saved_devices_backup.csv"):
      df_loaded = pd.read_csv("saved_devices_backup.csv", dtype=str)
      df_loaded.fillna("", inplace=True)
      st.session_state["device_data"] = df_loaded
  except:
    pass

# --- استرجاع سجلات الصيانة المحفوظة مسبقاً ---
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

# --- استرجاع أو تهيئة قائمة أعمال الصيانة المنسدلة المحفوظة ---
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


# دوال الحفظ على القرص الصلب
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


def save_devices_to_disk():
  if (
      "device_data" in st.session_state
      and st.session_state["device_data"] is not None
  ):
    st.session_state["device_data"].to_csv(
        "saved_devices_backup.csv", index=False
    )


# زر تصفير البيانات مخصص لصلاحيات "مدير النظام" فقط
if st.session_state["user_role"] == "مدير النظام (Admin)":
  st.sidebar.markdown("---")
  if st.sidebar.button("🗑️ تصفير ومسح كافة البيانات"):
    if "device_data" in st.session_state:
      del st.session_state["device_data"]
    if "maint_records" in st.session_state:
      st.session_state["maint_records"] = []
    if "maintenance_types" in st.session_state:
      st.session_state["maintenance_types"] = [
          "صيانة دورية",
          "إصلاح هاردوير",
          "فرمتة وترتيب نظام",
          "استبدال قطعة",
          "مشكلة شبكة",
      ]

    if os.path.exists("saved_devices_backup.csv"):
      os.remove("saved_devices_backup.csv")
    if os.path.exists("saved_maintenance_backup.csv"):
      os.remove("saved_maintenance_backup.csv")
    if os.path.exists("saved_maint_types.csv"):
      os.remove("saved_maint_types.csv")

    st.sidebar.success("تم تصفير كافة البيانات والملفات بنجاح!")
    st.rerun()

# --- محتوى الصفحات ---

if section == "لوحة المؤشرات (Dashboard)":
  st.title("📊 لوحة التحليلات والمؤشرات الشاملة")

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

    total_maintenance = 0
    total_cost = 0.0

    if "maint_records" in st.session_state and st.session_state["maint_records"]:
      total_maintenance = len(st.session_state["maint_records"])
      total_cost = sum(
          float(item.get("التكلفة ($)", 0.0))
          for item in st.session_state["maint_records"]
          if str(item.get("التكلفة ($)", 0.0)).strip() != ""
      )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
      st.metric(label="إجمالي الأجهزة", value=total_devices)
    with col2:
      st.metric(label="مهام الصيانة", value=total_maintenance)
    with col3:
      st.metric(label="إجمالي المصاريف", value=f"${total_cost:,.2f}")
    with col4:
      st.metric(label="الأقسام النشطة", value=active_departments)

    st.markdown("---")

    st.subheader("📈 الأجهزة حسب الأقسام")
    if dept_col:
      col_chart1, col_chart2 = st.columns(2)
      with col_chart1:
        dept_counts = df[dept_col].value_counts()
        st.bar_chart(dept_counts)
      with col_chart2:
        st.markdown(f"**تفاصيل توزيع الأجهزة حسب ({dept_col}):**")
        st.dataframe(dept_counts, use_container_width=True)
    else:
      st.info(
          "لم يتم العثور على عمود يحمل اسم 'القسم' بشكل صريح لإنشاء الرسم"
          " البياني."
      )

    st.markdown("---")
    st.subheader("📋 جداول البيانات المستوردة:")
    st.dataframe(df, use_container_width=True)

  else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
      st.metric(label="إجمالي الأجهزة", value="0")
    with col2:
      st.metric(label="مهام الصيانة", value="0")
    with col3:
      st.metric(label="إجمالي المصاريف", value="$0.00")
    with col4:
      st.metric(label="الأقسام النشطة", value="0")

    st.warning("⚠️ يرجى رفع ملف إكسل من الشريط الجانبي لعرض التحليلات.")

elif section == "إدارة الأجهزة والبيانات":
  st.title("💻 إدارة الأجهزة وملفات الموظفين وتعديل المواصفات")

  if (
      "device_data" in st.session_state
      and st.session_state["device_data"] is not None
  ):
    df = st.session_state["device_data"]

    if st.session_state["user_role"] == "مستعرض فقط (Viewer)":
      st.info(
          "👁️ أنت تستعرض البيانات فقط. صلاحيات التعديل أو الحذف معطلة لحسابك."
      )
      st.dataframe(df, use_container_width=True)
    else:
      st.info(
          "قم بتحديد أي صف من الجدول أدناه لعرض ملف الشخص وتعديل مواصفات جهازه"
          " مباشرة."
      )

      event_device = st.dataframe(
          df,
          use_container_width=True,
          selection_mode="single-row",
          on_select="rerun",
          key="device_table_selection",
      )

      selected_dev_rows = event_device.selection.get("rows", [])

      if selected_dev_rows:
        dev_index = selected_dev_rows[0]
        selected_person_data = df.iloc[dev_index]

        st.markdown("---")
        st.subheader(
            f"📄 ملف جهاز / موظف (الصف رقم {dev_index + 1}) - تعديل المواصفات"
        )

        with st.form("edit_device_specs_form"):
          updated_values = {}
          for col in df.columns:
            current_val = str(selected_person_data[col])
            if current_val == "nan":
              current_val = ""
            updated_values[col] = st.text_input(
                f"تعديل ({col})", value=current_val
            )

          col_save_dev, col_del_dev = st.columns(2)
          save_dev_btn = col_save_dev.form_submit_button(
              "💾 حفظ تعديلات المواصفات"
          )
          del_dev_btn = col_del_dev.form_submit_button(
              "🗑️ حذف هذا الجهاز من القائمة"
          )

          if save_dev_btn:
            for col, val in updated_values.items():
              df.loc[dev_index, col] = str(val)
            st.session_state["device_data"] = df
            save_devices_to_disk()
            st.success("تم تحديث وحفظ مواصفات الجهاز بنجاح!")
            st.rerun()

          if del_dev_btn:
            if st.session_state["user_role"] == "مدير النظام (Admin)":
              df = df.drop(index=dev_index).reset_index(drop=True)
              st.session_state["device_data"] = df
              save_devices_to_disk()
              st.success("تم حذف الجهاز بنجاح!")
              st.rerun()
            else:
              st.error("عذراً، صلاحياتك لا تسمح بحذف الأجهزة.")
  else:
    st.info("الرجاء رفع ملف الإكسل الخاص بالأجهزة من الشريط الجانبي أولاً.")

elif section == "🛠️ سجلات الصيانة":
  st.title("🛠️ سجلات أعمال الصيانة والإصلاحات")

  # قسم تعديل القائمة المنسدلة (متاح لمدير النظام فقط)
  if st.session_state["user_role"] == "مدير النظام (Admin)":
    with st.expander(
        "⚙️ إدارة وحذف عناصر القائمة المنسدلة (خاص بمدير النظام)"
    ):
      st.write(
          "قم بحذف السطر الذي يحتوي على الكلمة المراد إزالتها من الجدول أدناه،"
          " ثم اضغط على زر حفظ التعديلات:"
      )

      df_types_edit = pd.DataFrame(
          {"نوع الصيانة": st.session_state["maintenance_types"]}
      )
      edited_df_types = st.data_editor(
          df_types_edit,
          num_rows="dynamic",
          use_container_width=True,
          key="types_editor_table",
      )

      if st.button("💾 حفظ وحذف العناصر المحددة من القائمة"):
        new_types_list = (
            edited_df_types["نوع الصيانة"].dropna().astype(str).tolist()
        )
        new_types_list = [t.strip() for t in new_types_list if t.strip()]

        if new_types_list:
          st.session_state["maintenance_types"] = new_types_list
          save_maint_types_to_disk()
          st.success(
              "تم تحديث القائمة المنسدلة وحذف العناصر غير المطلوبة بنجاح!"
          )
          st.rerun()
        else:
          st.warning("يجب ألا تبقى القائمة فارغة تماماً!")

    st.markdown("---")

  # 1. عرض جدول السجلات أولاً
  if st.session_state["maint_records"]:
    st.subheader("📋 جدول سجلات الصيانة الحالية:")
    df_maint = pd.DataFrame(st.session_state["maint_records"])

    if st.session_state["user_role"] == "مستعرض فقط (Viewer)":
      st.info("👁️ عرض السجلات للمشاهدة فقط.")
      st.dataframe(df_maint, use_container_width=True)
    else:
      event = st.dataframe(
          df_maint,
          use_container_width=True,
          selection_mode="single-row",
          on_select="rerun",
          key="maint_table",
      )

      selected_rows = event.selection.get("rows", [])

      if selected_rows:
        selected_index = selected_rows[0]
        current_rec = st.session_state["maint_records"][selected_index]

        st.markdown("---")
        st.info(f"📄 نافذة تفاصيل وتعديل السجل رقم ({selected_index + 1})")

        edit_date = st.text_input(
            "تاريخ الصيانة", value=str(current_rec["تاريخ الصيانة"])
        )

        current_issue = str(current_rec["المشكلة"]).strip()
        if current_issue not in st.session_state["maintenance_types"]:
          st.session_state["maintenance_types"].append(current_issue)

        try:
          default_idx = st.session_state["maintenance_types"].index(
              current_issue
          )
        except:
          default_idx = 0

        edit_issue = st.selectbox(
            "نوع عمل الصيانة / المشكلة",
            options=st.session_state["maintenance_types"],
            index=default_idx,
            key=f"edit_issue_select_{selected_index}",
        )

        edit_action = st.text_input(
            "الإجراء المتخذ", value=str(current_rec["الإجراء"])
        )
        try:
          cost_val = float(current_rec["التكلفة ($)"])
        except:
          cost_val = 0.0

        edit_cost = st.number_input("التكلفة ($)", value=cost_val, step=5.0)
        edit_tech = st.text_input(
            "الفني المسؤول", value=str(current_rec["الفني"])
        )

        col_update, col_delete = st.columns(2)

        if col_update.button("💾 حفظ التعديلات"):
          st.session_state["maint_records"][selected_index] = {
              "تاريخ الصيانة": edit_date,
              "المشكلة": edit_issue,
              "الإجراء": edit_action,
              "التكلفة ($)": edit_cost,
              "الفني": edit_tech,
          }
          save_maintenance_to_disk()
          st.success("تم تحديث السجل وحفظه بنجاح!")
          st.rerun()

        if col_delete.button("🗑️ حذف هذا السجل"):
          if st.session_state["user_role"] == "مدير النظام (Admin)":
            st.session_state["maint_records"].pop(selected_index)
            save_maintenance_to_disk()
            st.success("تم حذف السجل بنجاح!")
            st.rerun()
          else:
            st.error("عذراً، صلاحياتك لا تسمح بحذف السجلات.")
  else:
    st.write("لا توجد سجلات صيانة مضافة حتى الآن.")

  # 2. نموذج تسجيل أعمال الصيانة الجديدة (يظهر فقط لمن يملك الصلاحية وليس للمستعرض)
  if st.session_state["user_role"] != "مستعرض فقط (Viewer)":
    st.markdown("---")
    with st.expander("➕ تسجيل عملية صيانة جديدة"):
      with st.form("maint_form"):
        m_date = st.date_input("تاريخ الصيانة", value=datetime.now())

        selected_issue_option = st.selectbox(
            "اختر عمل الصيانة (أو اكتب نوعاً جديداً أدناه إن لم يكن موجوداً):",
            options=st.session_state["maintenance_types"],
        )

        new_issue_input = st.text_input(
            "أو اكتب عمل صيانة جديد (سيتم حفظه تلقائياً في القائمة المنسدلة):", ""
        )

        action = st.text_input("الإجراء المتخذ والقطع المستبدلة")
        cost = st.number_input("التكلفة ($)", min_value=0.0, step=5.0)
        technician = st.text_input("اسم الفني المسؤول")

        submitted = st.form_submit_button("حفظ سجل الصيانة الجديد")
        if submitted:
          final_issue = (
              new_issue_input.strip()
              if new_issue_input.strip()
              else selected_issue_option
          )

          if (
              final_issue
              and final_issue not in st.session_state["maintenance_types"]
          ):
            st.session_state["maintenance_types"].append(final_issue)
            save_maint_types_to_disk()

          st.session_state["maint_records"].append({
              "تاريخ الصيانة": str(m_date),
              "المشكلة": final_issue,
              "الإجراء": action,
              "التكلفة ($)": cost,
              "الفني": technician,
          })
          save_maintenance_to_disk()
          st.success("تم تسجيل الصيانة وحفظها بنجاح! 🎉")
          st.rerun()