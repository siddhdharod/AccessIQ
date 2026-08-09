import datetime
import streamlit as st
import pandas as pd
from utils.helpers import init_session_state, inject_custom_css, load_dataset
from utils.booking_manager import (
    register_user, authenticate_user, update_user_profile,
    get_available_locations, get_slots_for_service, get_price,
    get_slot_availability_map, create_booking, cancel_booking,
    get_user_bookings, generate_qr_code_svg, PRICING_TABLE, DURATION_MINUTES
)
from utils.booking_pdf import generate_booking_pdf_receipt
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget

# 1. Page Configuration
st.set_page_config(
    page_title="Smart Booking - AccessIQ",
    page_icon="♿",
    layout="wide"
)

# 2. Session & Theme Initialization
init_session_state()
inject_custom_css()

# 3. Navbar & Sidebar Render
render_navbar()
df = load_dataset()
cities = df["City"].dropna().unique().tolist() if not df.empty and "City" in df.columns else []
controls = render_sidebar(cities)

# 4. Floating AI Chatbot Widget
render_chatbot_widget(controls["persona"])

# Initialize Booking Session State
if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

# Header Banner
st.markdown("""
<div class="page-transition">
    <div style="margin-bottom: 1.5rem;">
        <div class="hero-badge" style="display: inline-block; margin-bottom: 0.5rem;">
            ⚡ REAL-TIME ACCESSIBILITY RESERVATIONS
        </div>
        <h2 style="margin: 0; font-size: 2rem; font-weight: 800; color: var(--text-primary);">
            🎫 Smart Accessibility <span class="gradient-text">Booking Portal</span>
        </h2>
        <p style="color: var(--text-muted); font-size: 0.92rem; margin-top: 0.3rem;">
            Reserve guaranteed Wheelchairs (W01–W20) and Accessible Parking Slots (P01–P30) across public venues with real-time overlap prevention and digital QR gate passes.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_book, tab_history, tab_auth = st.tabs([
    "♿ Reserve Slot (Wheelchair & Parking)",
    "📜 Booking History & Receipts",
    "👤 Account Profile & Auth"
])

current_user = st.session_state.get("authenticated_user")

# ─────────────────────────────────────────────────────────────
# TAB 1: RESERVE SLOT (WHEELCHAIR & PARKING)
# ─────────────────────────────────────────────────────────────
with tab_book:
    if not current_user:
        st.warning("🔒 **Authentication Required:** You must be logged in to reserve accessibility slots. Please log in or create an account below.")
        
        c_login, c_signup = st.columns(2)
        with c_login:
            st.markdown("""
            <div class="glass-card">
                <h3 style="margin-top: 0; color: var(--text-primary);">🔑 Member Login</h3>
            """, unsafe_allow_html=True)
            with st.form("quick_login_form"):
                l_user = st.text_input("Username", key="q_l_user")
                l_pass = st.text_input("Password", type="password", key="q_l_pass")
                l_btn = st.form_submit_button("🚀 Log In", use_container_width=True)
                if l_btn:
                    user_data = authenticate_user(l_user, l_pass)
                    if user_data:
                        st.session_state["authenticated_user"] = user_data
                        st.success(f"Welcome back, {user_data['full_name'] or user_data['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")
            st.markdown("</div>", unsafe_allow_html=True)

        with c_signup:
            st.markdown("""
            <div class="glass-card">
                <h3 style="margin-top: 0; color: var(--text-primary);">📝 New Account Registration</h3>
            """, unsafe_allow_html=True)
            with st.form("quick_signup_form"):
                r_name = st.text_input("Full Name", key="q_r_name")
                r_user = st.text_input("Username", key="q_r_user")
                r_email = st.text_input("Email Address", key="q_r_email")
                r_phone = st.text_input("Phone Number", key="q_r_phone")
                r_pass = st.text_input("Password", type="password", key="q_r_pass")
                r_btn = st.form_submit_button("✨ Register Account", use_container_width=True)
                if r_btn:
                    ok, msg = register_user(r_user, r_email, r_pass, r_name, r_phone)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # User is Logged In - Booking Portal Interface
        locations = get_available_locations()
        prefilled_loc = st.session_state.get("prefill_booking_location", "")
        default_loc_idx = locations.index(prefilled_loc) if prefilled_loc in locations else 0

        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.85rem; color: var(--text-muted);">Logged in as:</span>
                    <span style="font-weight: 700; color: var(--primary-light); font-size: 1rem; margin-left: 0.4rem;">
                        👤 {current_user['full_name'] or current_user['username']} ({current_user['email']})
                    </span>
                </div>
                <div class="sidebar-status">
                    <div class="sidebar-status-dot"></div>
                    <span>Active Session</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.2, 1.8])

        with col_left:
            st.markdown("""
            <div class="glass-card">
                <h4 style="margin-top: 0; color: var(--text-primary); border-bottom: 1px solid var(--card-border); padding-bottom: 0.5rem;">
                    ⚙️ Reservation Parameters
                </h4>
            """, unsafe_allow_html=True)

            selected_location = st.selectbox(
                "🏢 Select Venue / Location",
                locations,
                index=default_loc_idx,
                key="booking_loc_select"
            )

            service_type = st.radio(
                "♿ Select Accessibility Service",
                ["Wheelchair Booking (20 Slots)", "Accessible Parking Booking (30 Slots)"],
                index=0,
                key="service_radio"
            )
            clean_service_type = "Wheelchair Booking" if "Wheelchair" in service_type else "Accessible Parking Booking"

            booking_date = st.date_input(
                "📅 Reservation Date",
                value=datetime.date.today(),
                min_value=datetime.date.today(),
                key="booking_date_picker"
            )

            # Generate 30-min time slots from 07:00 to 22:00
            time_options = []
            for h in range(7, 23):
                time_options.append(f"{h:02d}:00")
                time_options.append(f"{h:02d}:30")

            start_time_str = st.selectbox(
                "⏰ Start Time",
                time_options,
                index=4,  # default 09:00
                key="start_time_select"
            )

            durations = list(PRICING_TABLE[clean_service_type].keys())
            duration_str = st.selectbox(
                "⏳ Duration",
                durations,
                index=1,  # default 1 Hour
                key="duration_select"
            )

            # Calculate price
            calculated_price = get_price(clean_service_type, duration_str)

            st.markdown(f"""
            <div style="background: var(--bg-tertiary); border: 1px solid var(--primary); border-radius: var(--radius-md); padding: 0.9rem; margin-top: 1rem; text-align: center;">
                <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase;">Total Booking Rate</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: var(--primary-light); margin: 0.2rem 0;">
                    ₹{calculated_price:.0f} <span style="font-size: 0.9rem; color: var(--text-muted);">INR</span>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">
                    Includes all taxes, gate pass verification & instant cancellation release
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("""
            <div class="glass-card">
                <h4 style="margin-top: 0; color: var(--text-primary); border-bottom: 1px solid var(--card-border); padding-bottom: 0.5rem;">
                    🪑 Real-Time Slot Matrix & Selection
                </h4>
            """, unsafe_allow_html=True)

            # Fetch slot availability for selected time & location
            availability_map = get_slot_availability_map(
                selected_location, clean_service_type, booking_date, start_time_str, duration_str
            )

            available_slots = [slot for slot, is_free in availability_map.items() if is_free]
            booked_slots = [slot for slot, is_free in availability_map.items() if not is_free]

            st.markdown(f"""
            <div style="display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
                <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.82rem; color: #22c55e;">
                    🟢 Available ({len(available_slots)})
                </div>
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.82rem; color: #ef4444;">
                    🔴 Occupied / Booked ({len(booked_slots)})
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Slot Grid Visual Display
            slots_list = get_slots_for_service(clean_service_type)
            grid_cols = st.columns(6)
            for idx, slot_id in enumerate(slots_list):
                col = grid_cols[idx % 6]
                is_free = availability_map.get(slot_id, True)
                if is_free:
                    col.markdown(f"""
                    <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.5); border-radius: 8px; padding: 0.45rem; text-align: center; margin-bottom: 0.5rem; font-weight: 700; color: #22c55e; font-size: 0.85rem;">
                        {slot_id}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    col.markdown(f"""
                    <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 8px; padding: 0.45rem; text-align: center; margin-bottom: 0.5rem; font-weight: 700; color: #ef4444; font-size: 0.85rem; text-decoration: line-through;">
                        {slot_id}
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<hr style='border-color: var(--card-border); margin: 1rem 0;'>", unsafe_allow_html=True)

            if not available_slots:
                st.error("❌ No slots available for the chosen time window. Please change date or duration.")
            else:
                selected_slot = st.selectbox(
                    "🎯 Choose your slot ID",
                    available_slots,
                    key="slot_selector"
                )

                st.markdown(f"""
                <div style="background: var(--card-bg-hover); border: 1px dashed var(--primary); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1rem;">
                    <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem;">📋 Booking Summary Confirmation</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;">
                        • <b>Venue:</b> {selected_location}<br/>
                        • <b>Service:</b> {clean_service_type}<br/>
                        • <b>Selected Slot:</b> <span style="color: var(--primary-light); font-weight: 700;">{selected_slot}</span><br/>
                        • <b>Date & Time:</b> {booking_date} @ {start_time_str} ({duration_str})<br/>
                        • <b>Total Fee:</b> <span style="color: #22c55e; font-weight: 700;">₹{calculated_price:.0f} INR</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🚀 Confirm & Reserve Slot Now", key="confirm_booking_btn", use_container_width=True):
                    ok, msg, record = create_booking(
                        username=current_user["username"],
                        location_name=selected_location,
                        service_type=clean_service_type,
                        slot_id=selected_slot,
                        booking_date=booking_date,
                        start_time_str=start_time_str,
                        duration_str=duration_str
                    )

                    if ok and record:
                        st.balloons()
                        st.success(msg)
                        st.session_state["last_confirmed_booking"] = record
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("</div>", unsafe_allow_html=True)

        # Show Last Confirmed Receipt Card if available
        last_rec = st.session_state.get("last_confirmed_booking")
        if last_rec:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="section-header">
                <span>🎉 Booking Confirmation & Digital QR Pass</span>
                <div class="section-header-line"></div>
            </div>
            """, unsafe_allow_html=True)

            res_c1, res_c2 = st.columns([1.2, 1.8])
            with res_c1:
                qr_url = generate_qr_code_svg(f"ACCESSIQ:{last_rec['booking_id']}")
                st.markdown(f"""
                <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: 700;">DIGITAL ACCESS PASS QR</div>
                    <div style="margin: 1rem 0;">
                        <img src="{qr_url}" alt="QR Gate Pass" style="width: 140px; height: 140px; border-radius: 12px; background: white; padding: 8px; box-shadow: var(--shadow-md);">
                    </div>
                    <div style="font-weight: 700; color: var(--primary-light); font-size: 1.1rem;">{last_rec['booking_id']}</div>
                    <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.3rem;">Present QR code at gate entrance</div>
                </div>
                """, unsafe_allow_html=True)

            with res_c2:
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="margin-top: 0; color: #22c55e;">✔ Reservation Active</h4>
                    <div style="font-size: 0.88rem; color: var(--text-body); line-height: 1.6;">
                        <b>Venue:</b> {last_rec['location_name']}<br/>
                        <b>Service:</b> {last_rec['service_type']} (Slot: <b>{last_rec['slot_id']}</b>)<br/>
                        <b>Date:</b> {last_rec['booking_date']}<br/>
                        <b>Time:</b> {last_rec['start_time']} to {last_rec['end_time']} ({last_rec['duration_str']})<br/>
                        <b>Amount Paid:</b> ₹{last_rec['amount_inr']} INR
                    </div>
                </div>
                """, unsafe_allow_html=True)

                pdf_data = generate_booking_pdf_receipt(last_rec, current_user.get("full_name", ""))
                st.download_button(
                    label="📥 Download Official PDF Receipt",
                    data=pdf_data,
                    file_name=f"AccessIQ_Receipt_{last_rec['booking_id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# ─────────────────────────────────────────────────────────────
# TAB 2: BOOKING HISTORY & RECEIPTS
# ─────────────────────────────────────────────────────────────
with tab_history:
    if not current_user:
        st.info("🔒 Please log in to view your reservation history.")
    else:
        user_bookings = get_user_bookings(current_user["username"])
        st.markdown(f"""
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.8rem;">
            📜 Reservation Records for {current_user['full_name'] or current_user['username']} ({len(user_bookings)} Total)
        </div>
        """, unsafe_allow_html=True)

        if not user_bookings:
            st.info("You have no booking records yet. Use the 'Reserve Slot' tab above to create a booking.")
        else:
            for b in user_bookings:
                is_active = b.get("status") == "Active"
                status_color = "#22c55e" if is_active else "#ef4444"
                status_badge = f"<span style='background: rgba(34,197,94,0.15); color: {status_color}; border: 1px solid {status_color}; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;'>{b.get('status').upper()}</span>"

                st.markdown(f"""
                <div class="glass-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                        <div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary);">
                                {b.get('location_name')} • <span style="color: var(--primary-light);">{b.get('slot_id')}</span>
                            </div>
                            <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 0.2rem;">
                                {b.get('service_type')} | Date: <b>{b.get('booking_date')}</b> ({b.get('start_time')} - {b.get('end_time')})
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.3rem; font-weight: 800; color: var(--primary-light);">₹{b.get('amount_inr')} INR</div>
                            <div>{status_badge}</div>
                        </div>
                    </div>
                    <hr style="border-color: var(--card-border-subtle); margin: 0.7rem 0;">
                </div>
                """, unsafe_allow_html=True)

                c_dl, c_can = st.columns([1.5, 1])
                with c_dl:
                    pdf_bytes = generate_booking_pdf_receipt(b, current_user.get("full_name", ""))
                    st.download_button(
                        label=f"📥 Receipt PDF ({b.get('booking_id')})",
                        data=pdf_bytes,
                        file_name=f"Receipt_{b.get('booking_id')}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{b.get('booking_id')}"
                    )
                with c_can:
                    if is_active:
                        if st.button(f"❌ Cancel Booking ({b.get('booking_id')})", key=f"can_btn_{b.get('booking_id')}"):
                            ok_c, msg_c = cancel_booking(b.get("booking_id"), current_user["username"])
                            if ok_c:
                                st.success(msg_c)
                                st.rerun()
                            else:
                                st.error(msg_c)

# ─────────────────────────────────────────────────────────────
# TAB 3: ACCOUNT PROFILE & AUTH
# ─────────────────────────────────────────────────────────────
with tab_auth:
    if current_user:
        st.markdown(f"""
        <div class="glass-card">
            <h3 style="margin-top: 0; color: var(--text-primary);">👤 User Profile & Account Settings</h3>
            <p style="font-size: 0.85rem; color: var(--text-muted);">Manage your account details and profile information saved locally in AccessIQ.</p>
        """, unsafe_allow_html=True)

        with st.form("profile_update_form"):
            up_name = st.text_input("Full Name", value=current_user.get("full_name", ""))
            up_email = st.text_input("Email Address", value=current_user.get("email", ""))
            up_phone = st.text_input("Phone Number", value=current_user.get("phone", ""))
            up_btn = st.form_submit_button("💾 Save Profile Changes")
            if up_btn:
                ok, msg = update_user_profile(current_user["username"], up_name, up_phone, up_email)
                if ok:
                    st.session_state["authenticated_user"]["full_name"] = up_name
                    st.session_state["authenticated_user"]["email"] = up_email
                    st.session_state["authenticated_user"]["phone"] = up_phone
                    st.success(msg)
                else:
                    st.error(msg)

        st.markdown("<hr style='border-color: var(--card-border); margin: 1.2rem 0;'>", unsafe_allow_html=True)
        if st.button("🚪 Logout Account", key="logout_btn_tab", use_container_width=True):
            st.session_state["authenticated_user"] = None
            st.success("Successfully logged out.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("You are currently not logged in. Use Tab 1 or log in above.")

render_footer()
