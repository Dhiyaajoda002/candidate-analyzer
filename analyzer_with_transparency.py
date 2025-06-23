import streamlit as st
import openai
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="تحليل المرشحين + الشفافية", layout="centered")
st.title("🧠 أداة تحليل مرشحي الانتخابات + 🔍 محرك الشفافية السياسية")

tab1, tab2 = st.tabs(["📊 التحليل العام", "🔍 الشفافية السياسية"])

# ============ التبويب الأول: التحليل العام ==============
with tab1:
    api_key = st.text_input("🔑 أدخل مفتاح OpenAI API:", type="password")
    candidate1 = st.text_input("👤 أدخل اسم المرشح الأول (إجباري):")
    candidate2 = st.text_input("👤 أدخل اسم المرشح الثاني (اختياري):")

    def generate_analysis_prompt(name1, name2=None):
        base_points = """
        المحاور المطلوبة في التحليل:
        1. تحليل النبرة والتوجه الخطابي.
        2. تحليل شبكات التأثير (التحالفات، الداعمين، الخصوم).
        3. تحليل السمعة الإعلامية وتطورها.
        4. تقييم فرص الفوز بالاعتماد على الشعبية والدعم السياسي.
        5. تحليل التواجد الرقمي والتفاعل.
        6. 🧭 تحليل رادار المخاطر السياسية: هل المرشح قد يثير خلافات أو توترات؟
        7. 🔗 تحليل شبكة النفوذ السياسي: من يدعمه؟ من يعارضه؟ خصومات وتحالفات مؤثرة.
        8. 🚨 كشف التكرار أو التغير في المواقف بدون تفسير.
        """
        if name2:
            return f"قارن بين المرشحين '{name1}' و '{name2}' حسب النقاط التالية: {base_points}"
        else:
            return f"قم بتحليل شامل للمرشح '{name1}' حسب النقاط التالية: {base_points}"

    def generate_pdf(report_text, file_name="تقرير_التحليل.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('ArialUnicode', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        pdf.set_font("ArialUnicode", size=12)
        for line in report_text.split('\n'):
            pdf.multi_cell(0, 10, line)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        return temp_file.name

    if st.button("ابدأ التحليل العام"):
        if not api_key or not candidate1:
            st.warning("يرجى إدخال اسم مرشح واحد على الأقل ومفتاح API.")
        else:
            openai.api_key = api_key
            prompt = generate_analysis_prompt(candidate1, candidate2 if candidate2 else None)

            with st.spinner("⏳ جاري إجراء التحليل..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.6
                    )
                    analysis = response['choices'][0]['message']['content']
                    st.success("✅ التحليل جاهز:")
                    st.markdown(analysis)

                    pdf_path = generate_pdf(analysis)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 تحميل التقرير كـ PDF",
                            data=f,
                            file_name="تقرير_التحليل.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")

# ============ التبويب الثاني: الشفافية السياسية ==============
with tab2:
    st.subheader("🔍 تحليل الشفافية السياسية للمرشح")

    trans_api_key = api_key  # استخدام نفس مفتاح API
    trans_name = st.text_input("👤 اسم المرشح:")
    old_statement = st.text_area("📜 تصريح أو وعد سابق:")
    current_position = st.text_area("📌 موقفه أو سلوكه الحالي (إن توفر):")

    def generate_transparency_prompt(name, old, current):
        return f"""
        قم بتحليل مستوى الشفافية السياسية للمرشح "{name}" بناءً على المعلومات التالية:

        - التصريح أو الوعد السابق: "{old}"
        - الموقف الحالي أو ما تم تنفيذه: "{current}"

        حلل:
        1. هل الموقف الحالي يتفق مع التصريح السابق؟
        2. هل هناك تغير واضح؟ وهل تم شرحه؟
        3. هل التغير يُعتبر تراجعًا أم تطورًا طبيعيًا؟
        4. استنتج مؤشر الشفافية السياسي كنسبة مئوية.
        5. قدم ملاحظات موجزة تدعم هذا التقييم.
        """

    if st.button("🔍 تحليل الشفافية"):
        if not trans_api_key or not trans_name or not old_statement:
            st.warning("يرجى إدخال الاسم والتصريح السابق.")
        else:
            openai.api_key = trans_api_key
            prompt = generate_transparency_prompt(trans_name, old_statement, current_position)

            with st.spinner("⏳ جاري تقييم الشفافية..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.6
                    )
                    analysis = response['choices'][0]['message']['content']
                    st.success("✅ التقييم جاهز:")
                    st.markdown(analysis)

                    pdf_path = generate_pdf(analysis, "تقرير_الشفافية.pdf")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 تحميل تقرير الشفافية كـ PDF",
                            data=f,
                            file_name="تقرير_الشفافية.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
