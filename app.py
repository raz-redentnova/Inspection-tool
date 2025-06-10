import streamlit as st
import av
import cv2
import numpy as np
import os
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from inspection.visualization import get_contour_orientation
from inspection import processing, metrics, config_handler, image_acquisition, video_stream

st.set_page_config(layout="wide", page_title="Part Inspection System")

ROI_SIZE = 150
ROI_SCALE = 1

detection_methods = [
    "canny",
    "watershed",
    "otsu",
    "template_match"
]
config = config_handler.load_config("config.json")
method = config.get("detection_method", "canny")
if method not in detection_methods:
    method = "canny"

reference_contour = np.load("reference_contour.npy", allow_pickle=True) if os.path.exists("reference_contour.npy") else None
reference_moments = np.load("reference_moments.npy", allow_pickle=True) if os.path.exists("reference_moments.npy") else None
reference_fd = np.load("reference_fd.npy", allow_pickle=True) if os.path.exists("reference_fd.npy") else None
reference_roi = np.load("reference_roi.npy", allow_pickle=True) if os.path.exists("reference_roi.npy") else None
reference_orientation = np.load("reference_orientation.npy") if os.path.exists("reference_orientation.npy") else None
reference_direction = np.load("reference_direction.npy", allow_pickle=True) if os.path.exists("reference_direction.npy") else np.array([1.0, 0.0])

selected_metrics = config.get("selected_metrics", ["shape_score", "rotinv_moment_dist", "fourier_dist"])
thresholds = config.get("thresholds", {m: {"ok": 0.2, "nok": 0.5} for m in selected_metrics})

metric_labels = {
    "shape_score": "Shape Match (cv2.matchShapes)",
    "rotinv_moment_dist": "Rotation-Aligned Central Moment Distance",
    "fourier_dist": "Rotation-Aligned Fourier Descriptor Distance",
    "sift_score": "SIFT Similarity Score"
}

if "live_template_img" not in st.session_state:
    st.session_state["live_template_img"] = None

tab2, tab1 = st.tabs(["Live Inspection", "Parameter Tuning & Method Comparison"])

# -------------------- TAB 1 --------------------
with tab1:
    st.header("Testing and Method Comparison")

    # --- Top-of-tab inputs (always full width) ---------------------------
    uploaded_file = st.file_uploader("Upload an image for testing",
                                     type=["jpg", "jpeg", "png"])

    method_tab1 = st.selectbox("Detection Method",
                               detection_methods,
                               index=detection_methods.index(method))

    shape_metrics = ["shape_score", "rotinv_moment_dist",
                     "fourier_dist", "sift_score"]
    default_active = config.get("selected_metrics",
                                ["shape_score", "rotinv_moment_dist", "fourier_dist"])

    selected_metrics_tab1 = st.multiselect(
        "Metrics used for decision (select one or more):",
        [f"{m}: {metric_labels[m]}" for m in shape_metrics],
        default=[f"{m}: {metric_labels[m]}" for m in default_active],
    )
    selected_metrics_tab1 = [m.split(":")[0] for m in selected_metrics_tab1]

    # --- Three logical columns ------------------------------------------
    col_metrics, col_sliders, col_display = st.columns([0.25, 0.25, 0.50])

    # -- Centre column: sliders ------------------------------------------
    thresholds_tab1 = {}
    with col_sliders:
        st.markdown("### Threshold sliders")
        for m in selected_metrics_tab1:
            conf = config.get("thresholds", {}).get(m, {})
            ok_def  = conf.get("ok", 0.20 if m != "sift_score" else 0.20)
            nok_def = conf.get("nok", 0.50 if m != "sift_score" else 0.50)
            ok  = st.slider(f"{metric_labels[m]} OK ≤",  0.0, 1.0, ok_def,
                            0.01, key=f"{m}_ok")
            nok = st.slider(f"{metric_labels[m]} NOK >", 0.0, 1.0, nok_def,
                            0.01, key=f"{m}_nok")
            thresholds_tab1[m] = {"ok": ok, "nok": nok}

    # -- Prepare variables ------------------------------------------------
    contour = roi = overlay_up = None
    moment_result = {}
    mirrored_vertical = False
    metric_status = "N/A"

    # -- Process image when uploaded -------------------------------------
    if uploaded_file is not None:
        img  = image_acquisition.load_image_from_file(uploaded_file)
        roi, _ = processing.crop_center(img, ROI_SIZE, ROI_SIZE)
        contour, _, _ = processing.detect_contour(roi, method_tab1)

        moment_result = metrics.compute_metrics(
            contour, roi,
            reference_contour=reference_contour,
            reference_moments=reference_moments,
            reference_fd=reference_fd,
            reference_roi=reference_roi,
        )

        mirrored_vertical = processing.is_vertically_mirrored(contour)

        metric_status = metrics.classify_alignment(moment_result,
                                                   selected_metrics_tab1,
                                                   thresholds_tab1)
        if mirrored_vertical:
            metric_status = "NOK"

        overlay_up = processing.plot_roi_with_contour(
            roi, contour, metric_status,
            metrics_dict={m: moment_result.get(m) for m in selected_metrics_tab1},
            thresholds=thresholds_tab1,
            show_mirror_check=False,
        )

        if mirrored_vertical and overlay_up is not None:
            h, w = overlay_up.shape[:2]
            txt  = "MIRRORED - NOK"
            (tw, _), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
            cv2.putText(overlay_up, txt, (w - tw - 20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)

    # -- Left column: JSON + Metric status --------------------------------
    with col_metrics:
        st.markdown("#### Active thresholds")
        st.json({m: thresholds_tab1[m] for m in selected_metrics_tab1})

        st.markdown("### Metric Status")
        if overlay_up is None:
            st.info("Process an image to view metric results.")
        else:
            for m in selected_metrics_tab1:
                val = moment_result.get(m)
                ok  = thresholds_tab1[m]["ok"]
                nok = thresholds_tab1[m]["nok"]
                tag = "OK" if val <= ok else "NOK" if val > nok else "Suspicious"
                col = "green" if tag == "OK" else "red" if tag == "NOK" else "orange"
                st.markdown(
                    f"<span style='color:{col}'>{metric_labels[m]} ({m}): "
                    f"{val:.3f} — {tag}</span>",
                    unsafe_allow_html=True,
                )

    # -- Right column: image + buttons ------------------------------------
    with col_display:
        if overlay_up is not None:
            st.image(overlay_up, channels="BGR", use_column_width=True)

        # Buttons sit directly below the image
        btn_left, btn_right = st.columns(2)

        with btn_left:
            if st.button("Save current contour\nas reference"):
                if contour is None or roi is None:
                    st.error("Process an image first.")
                else:
                    angle, direction = get_contour_orientation(contour)
                    if direction[0] > 0:
                        contour = np.flip(contour, axis=1)
                        angle, direction = get_contour_orientation(contour)
                    np.save("reference_contour.npy", contour)
                    np.save("reference_moments.npy",
                            metrics.rotation_invariant_moments(contour))
                    np.save("reference_fd.npy",
                            metrics.compute_fourier_descriptor(contour))
                    np.save("reference_roi.npy", roi)
                    np.save("reference_orientation.npy", np.array([angle]))
                    np.save("reference_direction.npy", direction)
                    st.success("Reference saved.")

        with btn_right:
            if st.button("Save preferred\nmethod & thresholds"):
                config_handler.save_config("config.json", {
                    "detection_method": method_tab1,
                    "thresholds": thresholds_tab1,
                    "selected_metrics": selected_metrics_tab1,
                })
                st.success("Config updated.")


# -------------------- TAB 2 — Live Inspection --------------------
with tab2:
    # ── auto-start flag (only once) ───────────────────────────────────
    if "live_started" not in st.session_state:
        st.session_state["live_started"] = True      # auto-start on first load

    # ── optional template upload (template_match mode) ────────────────
    if method == "template_match":
        st.info("Upload a template image for live matching.")
        live_template_file = st.file_uploader(
            "Live Template Image (Tab 2)",
            type=["jpg", "jpeg", "png"],
            key="live_template",
        )
        if live_template_file is not None:
            st.session_state["live_template_img"] = image_acquisition.load_image_from_file(
                live_template_file
            )
        else:
            st.session_state["live_template_img"] = None
    else:
        st.session_state["live_template_img"] = None

    # ── InspectionProcessor (unchanged except mirror call) ────────────
    class InspectionProcessor(VideoProcessorBase):
        def __init__(self):
            self.template = None
            self.raw_roi = None
            self.metric_history = []
            self.n_average = 20
            self.latest_overlay = None
            self.latest_status  = None
            self.latest_metrics = None

        def set_template(self, template_img):
            self.template = template_img

        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")

            # 1. crop centre
            roi, _ = processing.crop_center(img, ROI_SIZE, ROI_SIZE)
            self.raw_roi = roi.copy()

            # 2. detect contour
            tmpl = self.template if method == "template_match" else None
            contour, _, _ = processing.detect_contour(roi, method, tmpl)

            # 3. compute metrics
            moment_result = metrics.compute_metrics(
                contour, roi,
                reference_contour=reference_contour,
                reference_moments=reference_moments,
                reference_fd=reference_fd,
                reference_roi=reference_roi,
            )

            # 4. mirror check (side-span rule)
            mirrored_vertical = processing.is_vertically_mirrored(contour)

            # 5. running-average metrics
            metrics_dict = {m: moment_result.get(m) for m in selected_metrics}
            self.metric_history.append(metrics_dict)
            if len(self.metric_history) > self.n_average:
                self.metric_history.pop(0)

            avg_metrics = {
                m: float(np.mean([d[m] for d in self.metric_history if d[m] is not None]))
                if any(d[m] is not None for d in self.metric_history) else None
                for m in selected_metrics
            }

            metric_status = metrics.classify_alignment(avg_metrics, selected_metrics, thresholds)
            if mirrored_vertical:
                metric_status = "NOK"

            # 6. build overlay
            overlay = processing.plot_roi_with_contour(
                roi, contour, metric_status,
                metrics_dict=avg_metrics,
                thresholds=thresholds,
                show_mirror_check=False,
            )

            if mirrored_vertical:
                h, w = overlay.shape[:2]
                txt  = "MIRRORED - NOK"
                (tw, _), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                cv2.putText(overlay, txt, (w - tw - 20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)

            self.latest_overlay = overlay
            self.latest_status  = metric_status
            self.latest_metrics = avg_metrics

            return av.VideoFrame.from_ndarray(overlay, format="bgr24")

    # factory for streamer
    def processor_factory():
        proc = InspectionProcessor()
        if method == "template_match":
            proc.set_template(st.session_state.get("live_template_img"))
        return proc

    # ── layout: capture | video | side - (0.25 / 0.50 / 0.25) ───────────
    col_capture, col_vid, col_side = st.columns([0.25, 0.50, 0.25])

    # determine if streaming is allowed
    template_needed  = method == "template_match" and st.session_state.get("live_template_img") is None
    stream_disabled  = template_needed or not st.session_state["live_started"]

    if template_needed:
        st.warning("Upload a template image before streaming starts.")

    # ── video (centre) ─────────────────────────────────────────────────
    webrtc_ctx = None
    with col_vid:
        if not stream_disabled:
            webrtc_ctx = webrtc_streamer(
                key="inspection",
                video_processor_factory=processor_factory,
                media_stream_constraints={
                    "video": {
                        "width":  {"ideal": 1280},
                        "height": {"ideal": 720},
                        "frameRate": {"ideal": 5, "max": 5},
                    },
                    "audio": False,
                },
                async_processing=True,
                rtc_configuration={
                    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                },
            )
        else:
            st.empty()   # keep layout

    # ── capture button (left) ──────────────────────────────────────────
    with col_capture:
        if st.button("Capture frame", disabled=stream_disabled):
            frame_to_save = None
            if webrtc_ctx and hasattr(webrtc_ctx, "video_processor") \
                    and webrtc_ctx.video_processor:
                frame_to_save = webrtc_ctx.video_processor.raw_roi

            if frame_to_save is not None:
                pics_dir = "pics"
                os.makedirs(pics_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = os.path.join(pics_dir, f"capture_{ts}.png")
                cv2.imwrite(fname, frame_to_save)
                st.success(f"Frame saved: {fname}")
            else:
                st.error("Frame not available yet – wait for video to start.")
