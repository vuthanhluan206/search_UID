
"""Public Locket username-to-UID lookup prototype for Vercel.

The Locket endpoint is undocumented. Only a valid, authorized session can
access it; this code does not acquire or bypass upstream authentication.
"""
import os
import re
from urllib.parse import urlsplit, unquote

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Locket UID Lookup Lab",
    version="1.1.0",
    docs_url=None,
    redoc_url=None
)

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,40}$")

ALLOWED_DOMAINS = {
    "locket.cam",
    "www.locket.cam",
    "locket.camera",
    "www.locket.camera"
}

UPSTREAM = "https://api.locketcamera.com/getUserByUsername"


class LookupRequest(BaseModel):
    value: str = Field(min_length=1, max_length=300)


def parse_username(value: str) -> str:
    raw = value.strip()

    if raw.startswith(("https://", "http://")):
        parsed = urlsplit(raw)

        if (
            parsed.scheme != "https"
            or parsed.hostname not in ALLOWED_DOMAINS
            or parsed.username
            or parsed.password
            or parsed.port
        ):
            raise ValueError(
                "Chỉ chấp nhận link HTTPS thuộc locket.cam hoặc locket.camera"
            )

        parts = [
            unquote(part)
            for part in parsed.path.split("/")
            if part
        ]

        if len(parts) != 1:
            raise ValueError(
                "Chỉ hỗ trợ link hồ sơ như https://locket.cam/vt.l"
            )

        raw = parts[0]

    elif (
        "/" in raw
        or ":" in raw
        or "?" in raw
        or "#" in raw
    ):
        raise ValueError(
            "Hãy nhập username hoặc link hồ sơ hợp lệ"
        )

    if raw.startswith("@"):
        raw = raw[1:]

    if not USERNAME_RE.fullmatch(raw):
        raise ValueError("Username không hợp lệ")

    return raw


def get_uid(obj):
    """Read known response layouts without guessing identifiers."""

    if not isinstance(obj, dict):
        return None

    candidates = [
        obj,
        obj.get("data"),
        obj.get("result")
    ]

    result = obj.get("result")

    if isinstance(result, dict):
        candidates.append(result.get("data"))

    for item in candidates:
        if isinstance(item, dict):
            for key in ("uid", "user_uid", "userUid"):
                found = item.get(key)

                if (
                    isinstance(found, str)
                    and 5 <= len(found) <= 128
                ):
                    return found

    return None


@app.get("/", response_class=HTMLResponse)
def homepage():
    return """<!doctype html>
<html lang='vi'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>

<title>Locket UID Lookup</title>

<style>
:root {
    font-family: system-ui,-apple-system,Segoe UI,sans-serif;
    color-scheme: light;
}

body {
    margin: 0;
    background: #f5f7fb;
    color: #152039;
    display: grid;
    place-items: center;
    min-height: 100vh;
    padding: 20px;
    box-sizing: border-box;
}

main {
    width: min(100%,510px);
    background: white;
    border: 1px solid #e1e5ef;
    border-radius: 18px;
    padding: 28px;
    box-sizing: border-box;
    box-shadow: 0 12px 40px #0c21400d;
}

h1 {
    font-size: 25px;
    margin: 0 0 8px;
}

p {
    color: #58647a;
    line-height: 1.6;
}

label {
    display: block;
    font-weight: 650;
    margin: 20px 0 7px;
}

input {
    box-sizing: border-box;
    width: 100%;
    padding: 13px 14px;
    border: 1px solid #cbd3e2;
    border-radius: 10px;
    font-size: 16px;
}

button {
    width: 100%;
    border: 0;
    background: #155eef;
    color: white;
    padding: 14px;
    border-radius: 10px;
    font-weight: 700;
    cursor: pointer;
    margin-top: 22px;
    font-size: 16px;
}

button:disabled {
    opacity: .55;
    cursor: wait;
}

pre {
    white-space: pre-wrap;
    word-break: break-word;
    padding: 15px;
    border-radius: 10px;
    background: #f0f4fb;
    min-height: 26px;
    font-size: 14px;
}

small {
    color: #607089;
}

code {
    font-family: ui-monospace,monospace;
}
</style>
</head>

<body>
<main>
    <h1>Tìm UID Locket</h1>

    <p>
        Tra cứu UID bằng username hoặc link hồ sơ Locket.
        API này <strong>không chính thức</strong>
        và có thể từ chối yêu cầu.
    </p>

    <form id='f'>
        <label for='value'>Link Locket hoặc username</label>

        <input
            id='value'
            required
            maxlength='300'
            placeholder='https://locket.cam/vt.l'
            value='https://locket.cam/vt.l'
        >

        <button id='b' type='submit'>
            Tra cứu UID
        </button>
    </form>

    <label>Kết quả</label>

    <pre id='out'>Chưa tra cứu.</pre>

    <small>
        Không nhập mật khẩu Locket, mã OTP hay token đăng nhập
        vào biểu mẫu.
    </small>
</main>

<script>
const f = document.getElementById('f');
const out = document.getElementById('out');
const b = document.getElementById('b');

f.addEventListener('submit', async e => {
    e.preventDefault();

    b.disabled = true;
    out.textContent = 'Đang tra cứu…';

    try {
        const r = await fetch('/api/lookup', {
            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                value: document.getElementById('value').value
            })
        });

        const j = await r.json();

        out.textContent = JSON.stringify(j, null, 2);

        if (!r.ok) {
            out.textContent += '\\nHTTP ' + r.status;
        }

    } catch (err) {
        out.textContent = 'Lỗi kết nối: ' + err.message;
    } finally {
        b.disabled = false;
    }
});
</script>

</body>
</html>"""


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "locket-uid-lookup",
        "lookup_configured": bool(
            os.getenv("LOCKET_BEARER_TOKEN")
        )
    }


@app.post("/api/lookup")
async def lookup(payload: LookupRequest):
    # Public endpoint: no LOOKUP_ADMIN_KEY required.

    try:
        username = parse_username(payload.value)

    except ValueError as ex:
        raise HTTPException(
            status_code=422,
            detail=str(ex)
        ) from ex

    bearer = os.getenv(
        "LOCKET_BEARER_TOKEN", ""
    ).strip()

    if not bearer:
        return {
            "username": username,
            "uid": None,
            "status": "not_configured",
            "message": (
                "Đã tách username. Chưa có phiên API "
                "Locket được cấp phép (LOCKET_BEARER_TOKEN)."
            )
        }

    # No DNS overrides, MITM proxies, fake AppCheck tokens,
    # or credential scraping.
    # HTTPS to the official hostname;
    # use only a legitimately authorized session.

    try:
        async with httpx.AsyncClient(
            timeout=12.0,
            follow_redirects=False,
            trust_env=False
        ) as client:

            response = await client.post(
                UPSTREAM,

                json={
                    "data": {
                        "username": username
                    }
                },

                headers={
                    "Authorization": f"Bearer {bearer}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Locket không phản hồi kịp thời"
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Không kết nối được với Locket API"
        )

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=403,
            detail=(
                "Locket từ chối phiên hoặc yêu cầu App Check; "
                "không thể tự động lấy UID"
            )
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=(
                "Không tìm thấy tài khoản hoặc endpoint "
                "không còn khả dụng"
            )
        )

    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail="Locket giới hạn yêu cầu. Hãy thử lại sau"
        )

    if not response.is_success:
        raise HTTPException(
            status_code=502,
            detail=f"Locket API trả HTTP {response.status_code}"
        )

    try:
        obj = response.json()

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="Locket không trả JSON hợp lệ"
        )

    uid = get_uid(obj)

    if not uid:
        return {
            "username": username,
            "uid": None,
            "status": "uid_not_found",
            "message": (
                "API có phản hồi nhưng không có UID theo "
                "các cấu trúc đã nhận diện; không suy đoán UID."
            )
        }

    return {
        "username": username,
        "uid": uid,
        "status": "resolved",
        "source": "unofficial_locket_api"
    }
