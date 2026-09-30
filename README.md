# Bộ công cụ giảng dạy VLUTE

Trang cổng (hub) tập hợp các công cụ giảng dạy chạy trên trình duyệt. Hub được
deploy trên Vercel; API thống kê lượt truy cập lưu số liệu dùng chung trong Upstash Redis.

## Cấu trúc thư mục

```
vlute-hub/
├── index.html          ← trang cổng (danh sách công cụ)
├── CREATE_LESSON.html   ← Soạn bài giảng → SCORM
├── CREATE_QUIZ.html     ← Tạo ngân hàng câu hỏi E-VLUTE
├── PROCESS_MARK.html    ← Xử lý điểm thành phần
├── api/visits.js        ← API ghi nhận lượt truy cập trên Vercel
├── vercel.json         ← cấu hình web tĩnh (tùy chọn)
└── README.md
```

## Chạy thử ở máy

Mở trực tiếp `index.html` hoặc chạy server tĩnh chỉ xem giao diện. Để kiểm tra
thống kê lượt truy cập, cần chạy qua Vercel CLI và cấu hình biến môi trường như
hướng dẫn bên dưới.

```bash
npx serve .
# hoặc
python3 -m http.server 8080
```

## Deploy lên Vercel

**Cách 1 — kéo–thả (nhanh nhất):** vào https://vercel.com → New Project →
kéo cả thư mục `vlute-hub` vào, hoặc dùng CLI:

```bash
npm i -g vercel
cd vlute-hub
vercel        # xem thử (preview)
vercel --prod # deploy chính thức
```

**Cách 2 — qua GitHub:** đẩy thư mục này lên một repo GitHub → Vercel → Import
repo. Vercel tự nhận đây là static site (không cần Framework, Build Command để trống).

### Bật thống kê lượt truy cập dùng chung

1. Tạo một database Redis trên Upstash và lấy **REST URL** cùng **REST token**.
2. Trong Vercel, mở **Project Settings → Environment Variables**, thêm:
  - `UPSTASH_REDIS_REST_URL`
  - `UPSTASH_REDIS_REST_TOKEN`
3. Chọn môi trường cần dùng (Production và/hoặc Preview), lưu biến môi trường rồi
  deploy lại project.
1. Trong Vercel project, mở **Storage** và xác nhận Redis database đã được link
  với project; biến REST URL/token phải có trong **Settings → Environment
  Variables** cho môi trường **Production**.
2. API tự đọc các tên biến Vercel Storage thường tạo như
  `storage_KV_REST_API_URL` và `storage_KV_REST_API_TOKEN`. Cũng hỗ trợ
  `KV_REST_API_URL`/`KV_REST_API_TOKEN` và
  `UPSTASH_REDIS_REST_URL`/`UPSTASH_REDIS_REST_TOKEN`. Không cần tạo thêm biến
  nếu project đã có đủ cặp REST URL/token.
3. Nếu vừa link storage hoặc vừa thêm biến, redeploy production mới nhất (hoặc
  push commit mới lên `main`) để Function nhận môi trường mới. Không commit
  URL/token Redis vào GitHub.

API `/api/visits` tăng lượt truy cập mỗi lần trang chủ được tải và lưu riêng số
trong ngày/tháng theo múi giờ Việt Nam. Các máy và trình duyệt sẽ đọc chung số
liệu; đây là lượt xem trang, không phải số khách truy cập duy nhất. Nếu chưa cấu
hình Redis, giao diện hiển thị `-` cho hai số thống kê.

## Thêm một công cụ mới (khoảng 1 phút)

1. Copy file `.html` của công cụ mới vào **cùng thư mục** với `index.html`.
2. Mở `index.html`, tìm mảng `TOOLS` (có chú thích rõ), thêm một khối:

```js
{
  code:"TÊN NGẮN",                 // nhãn mono trên thẻ, vd "SCORM"
  name:"Tên công cụ đầy đủ",
  role:"Mô tả vai trò · 1 dòng",
  desc:"Mô tả ngắn 1–2 câu về công cụ.",
  tags:["Từ khóa 1","Từ khóa 2"],
  file:"TEN_FILE.html",            // đúng tên file vừa copy vào
  accent:"teal",                   // teal | clay | green | amber
  cat:"content",                   // content | assess | grade
  status:"ready",                  // ready = mở được, soon = hiện mờ "sắp có"
  icon:'<path d="..."/>'           // SVG path (stroke), có thể để tạm icon cũ
}
```

3. Lưu lại và deploy lại. Trang tự render thẻ mới, tự đếm số lượng, tự lọc theo
   danh mục và ô tìm kiếm — không phải sửa gì thêm.

### Thêm danh mục mới

Sửa mảng `CATS` ở đầu `<script>` trong `index.html`, rồi dùng `id` danh mục đó
ở trường `cat` của công cụ.

## Ghi chú

- `PROCESS_MARK.html` có tham chiếu ảnh `logo-vlute(960).png`. Nếu muốn hiện logo,
  copy file ảnh đó vào cùng thư mục. Không có ảnh thì công cụ vẫn chạy bình thường.
- Các công cụ lưu nháp bằng bộ nhớ trình duyệt của người dùng; không có dữ liệu
  nào gửi lên máy chủ.
