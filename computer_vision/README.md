# Computer Vision Module

Phase 1 did not identify a licensed, production-quality image/video dataset for PPE, smoke, fire, fall, restricted-area, worker-counting, or vehicle-detection training.

The platform therefore exposes the computer-vision module boundary and API status, but does not train or fake CV models.

Recommended production path:

- Use a pretrained detector such as YOLO/RT-DETR only after dependency and license approval.
- Fine-tune with consented site CCTV or a clearly licensed PPE dataset.
- Store video-derived events as `risk_events` with frame/time/source metadata.
- Require privacy review before face, identity, or worker-tracking deployment.

