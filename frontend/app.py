import streamlit as st

pages = {
    "SilkMoth": [
        st.Page("pages/what_is_silkmoth.py", title="What is SilkMoth?"),
        st.Page("pages/inclusion_dependency_view.py", title="Inclusion Dependency Experiment"),
        st.Page("pages/dataset_view.py", title="Our Datasets"),
    ],

}

pg = st.navigation(pages)
pg.run()