# Privacy Policy — ShareGuard

> **Last updated:** 2026-05-08
> **App:** ShareGuard — "Sạch khi gửi — tôn trọng creator."
> **Developer:** snailb1007
> **Contact:** [GitHub Issues](https://github.com/snailb1007/ShareGuard-Public/issues)

---

## Summary

ShareGuard is a privacy-first Android app that strips metadata and tracking parameters from shared content. **We collect zero personal data.** All processing happens entirely on your device.

---

## 1. No Personal Information Collection

ShareGuard does **not** collect, store, transmit, or sell any personally identifiable information (PII). Specifically:

- **No accounts.** No login, no registration, no email collection.
- **No analytics.** No Firebase Analytics, Google Analytics, Crashlytics, or any third-party tracking SDK.
- **No advertising.** No ad SDKs, no ad identifiers, no behavioral profiling.
- **No crash reporting.** No automated crash report uploads of any kind.

---

## 2. Local-Only Processing

All content processing — including metadata stripping, URL parameter cleaning, and redirect unwrapping — occurs **entirely on your device**. ShareGuard never uploads your photos, videos, documents, or URLs to any server.

- **Images:** EXIF, IPTC, and XMP metadata are stripped locally using AndroidX ExifInterface.
- **Videos:** MP4 atom stripping occurs without re-encoding, entirely on-device.
- **Documents:** PDF and Office metadata are parsed and stripped locally.
- **URLs:** Tracking parameters are removed and redirect chains are unwrapped using a local rule engine.

No content — original or cleaned — ever leaves your device through ShareGuard.

---

## 3. History Data

ShareGuard maintains a local history of cleaning operations for your convenience. This history stores **metadata only**:

- Content type (image, video, URL, document)
- Timestamp of the operation
- Count of stripped metadata fields / parameters

**History never stores:**
- The original file or its contents
- The cleaned file or its contents
- File names, file paths, or URIs
- Any data extracted during stripping (GPS coordinates, device info, etc.)

History is automatically purged after 30 days (configurable in Settings). You can manually clear all history at any time.

---

## 4. Rule Updates

ShareGuard periodically checks for updated URL stripping rules to catch new trackers. These updates:

- Use a standard HTTPS GET request with ETag caching
- **Send no user identifier, device ID, or any personal information**
- Contain no cookies or authentication tokens
- Are verified using Ed25519 cryptographic signatures
- Are cross-validated from two independent origins (CDN and GitHub)

If an update fails verification, ShareGuard keeps its current rules. Bundled fallback rules are always available in the app.

---

## 5. Permissions

ShareGuard requests only the minimum permissions necessary:

| Permission | Purpose |
|---|---|
| `INTERNET` | Download rule updates only |
| Read shared content (via Share Sheet) | Process content shared by user to strip metadata |

ShareGuard does **not** request:
- Location access
- Camera or microphone access
- Contacts or calendar access
- Phone state or call log access
- Background location or activity recognition

---

## 6. Third-Party Services

ShareGuard uses **no** third-party services that collect user data. The only network communication is the rule update mechanism described in Section 4.

---

## 7. Children's Privacy

ShareGuard does not knowingly collect any information from anyone, including children under 13. Since no data is collected from any user, ShareGuard is compliant with COPPA and similar regulations.

---

## 8. Transparency & Security

ShareGuard is designed from the ground up to protect your privacy. While the app is not open source, its core architecture strictly enforces local-only processing. We rely on standard Android security mechanisms to ensure that the data processed by ShareGuard remains sandboxed and inaccessible to external entities.

---

## 9. Changes to This Policy

If we update this privacy policy, the updated version will be posted to this page with a new "Last updated" date. Since ShareGuard collects no data, changes would typically relate to new features or clarifications.

---

## 10. Contact

For questions or concerns about this privacy policy, please open an issue on our public GitHub repository:

[https://github.com/snailb1007/ShareGuard-Public/issues](https://github.com/snailb1007/ShareGuard-Public/issues)
