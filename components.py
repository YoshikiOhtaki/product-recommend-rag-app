"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import os
import streamlit as st
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown("こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。")
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """
    商品情報の表示

    Args:
        result: Retrieverから返されたDocumentリスト
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    if not result:
        raise ValueError("検索結果が空です。")

    page_content = result[0].page_content
    product_lines = page_content.split("\n")

    product = {}
    for line in product_lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            normalized_key = key.strip().replace("\ufeff", "")
            product[normalized_key] = value.strip()

    logger.info({"parsed_product": product})

    st.markdown("以下の商品をご提案いたします。")

    # 商品名と価格
    st.success(
        f"""
商品名：{product.get('name', '不明')}（商品ID: {product.get('id', '不明')}）

価格：{product.get('price', '不明')}
"""
    )

    # 在庫状況
    stock_status = product.get("stock_status", "")

    if stock_status == ct.STOCK_STATUS_LOW:
        st.warning(ct.STOCK_WARNING_MESSAGE, icon=ct.STOCK_WARNING_ICON)
    elif stock_status == ct.STOCK_STATUS_NONE:
        st.error(ct.STOCK_ERROR_MESSAGE, icon=ct.STOCK_ERROR_ICON)

    # 商品カテゴリ、メーカー、評価
    st.code(
        f"""
商品カテゴリ：{product.get('category', '不明')}

メーカー：{product.get('maker', '不明')}

評価：{product.get('score', '不明')}({product.get('review_number', '不明')}件)
""",
        language=None,
        wrap_lines=True
    )

    # 商品画像
    image_file_name = product.get("file_name", "")
    image_path = os.path.join("images", "products", image_file_name)

    if image_file_name and os.path.exists(image_path):
        st.image(image_path, width=400)
    else:
        logger.warning(f"商品画像が見つかりません: {image_path}")
        st.warning(f"商品画像が見つかりません: {image_path}")

    # 商品説明
    st.code(
        product.get("description", "商品説明がありません。"),
        language=None,
        wrap_lines=True
    )

    # おすすめ対象ユーザー
    st.markdown("**こんな方におすすめ！**")
    st.info(product.get("recommended_people", "情報がありません。"))

    # 商品ページリンク
    st.link_button(
        "商品ページを開く",
        type="primary",
        use_container_width=True,
        url="https://google.com"
    )