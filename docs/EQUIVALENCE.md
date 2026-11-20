# Chứng Minh Tính Tương Đương (Equivalence Proof)

Báo cáo kiểm thử trung thành với bản gốc Princeton algs4.
Mỗi phép đo so sánh bản gốc (chạy qua reflection để bỏ shuffle ngẫu nhiên với Quick) và bản biến thể trên cùng một mảng đối tượng `CountingInteger`.

## 1. Tiêu chuẩn đánh giá:
- **Số so sánh (Compare Count)**: Số lần gọi `compareTo` phải trùng khớp 100%.
- **Rolling Hash**: Hash chạy 64-bit của chuỗi cặp phần tử được so sánh theo đúng thứ tự gọi phải trùng khớp 100% (chứng minh đường đi thực thi y hệt).
- **Mảng kết quả**: Từng phần tử của mảng sau sắp xếp phải hoàn toàn giống nhau.

## 2. Bảng kết quả tổng hợp (Mẫu đại diện Seed=42):

| Thuật toán | Phân phối | N | Tham số m | So sánh Gốc | So sánh Biến thể | Khớp số? | Hash Gốc | Hash Biến thể | Khớp Hash? | Kết quả mảng |
|:---|:---|---:|---:|---:|---:|:---:|---:|---:|:---:|:---:|
| Merge vs MergeCutoff | Random | 10 | 1 | 73 | 73 | YES | 5974006658222335852 | 5974006658222335852 | YES | MATCH |
| Quick vs QuickCutoff | Random | 10 | 1 | 76 | 76 | YES | -605349243464727368 | -605349243464727368 | YES | MATCH |
| MergeX vs MergeXParam | Random | 10 | 7 | 47 | 47 | YES | -3807110852257524016 | -3807110852257524016 | YES | MATCH |
| QuickX vs QuickXParam | Random | 10 | 8 | 42 | 42 | YES | -3184882632381782600 | -3184882632381782600 | YES | MATCH |
| Merge vs MergeCutoff | Random | 50 | 1 | 696 | 696 | YES | -6639137991577787531 | -6639137991577787531 | YES | MATCH |
| Quick vs QuickCutoff | Random | 50 | 1 | 640 | 640 | YES | 1544740277313551207 | 1544740277313551207 | YES | MATCH |
| MergeX vs MergeXParam | Random | 50 | 7 | 556 | 556 | YES | -7615329908247058003 | -7615329908247058003 | YES | MATCH |
| QuickX vs QuickXParam | Random | 50 | 8 | 346 | 346 | YES | 7648011723705488042 | 7648011723705488042 | YES | MATCH |
| Merge vs MergeCutoff | Random | 100 | 1 | 1694 | 1694 | YES | 3484403155806136621 | 3484403155806136621 | YES | MATCH |
| Quick vs QuickCutoff | Random | 100 | 1 | 1518 | 1518 | YES | -4397849675612242586 | -4397849675612242586 | YES | MATCH |
| MergeX vs MergeXParam | Random | 100 | 7 | 1426 | 1426 | YES | 7807452910065771680 | 7807452910065771680 | YES | MATCH |
| QuickX vs QuickXParam | Random | 100 | 8 | 849 | 849 | YES | 6938098472365400929 | 6938098472365400929 | YES | MATCH |
| Merge vs MergeCutoff | Random | 500 | 1 | 11855 | 11855 | YES | -7141579183030221785 | -7141579183030221785 | YES | MATCH |
| Quick vs QuickCutoff | Random | 500 | 1 | 11024 | 11024 | YES | -8953370668781651128 | -8953370668781651128 | YES | MATCH |
| MergeX vs MergeXParam | Random | 500 | 7 | 10433 | 10433 | YES | 139041871188327359 | 139041871188327359 | YES | MATCH |
| QuickX vs QuickXParam | Random | 500 | 8 | 5621 | 5621 | YES | 6508791389092439611 | 6508791389092439611 | YES | MATCH |
| Merge vs MergeCutoff | Random | 1000 | 1 | 26685 | 26685 | YES | 3873882188831734274 | 3873882188831734274 | YES | MATCH |
| Quick vs QuickCutoff | Random | 1000 | 1 | 24378 | 24378 | YES | 5602646047800959307 | 5602646047800959307 | YES | MATCH |
| MergeX vs MergeXParam | Random | 1000 | 7 | 23852 | 23852 | YES | 2658971580098229834 | 2658971580098229834 | YES | MATCH |
| QuickX vs QuickXParam | Random | 1000 | 8 | 11738 | 11738 | YES | -7992077031392881440 | -7992077031392881440 | YES | MATCH |
| Merge vs MergeCutoff | Sorted | 10 | 1 | 69 | 69 | YES | -6578461758339580507 | -6578461758339580507 | YES | MATCH |
| Quick vs QuickCutoff | Sorted | 10 | 1 | 108 | 108 | YES | -4797111356509842696 | -4797111356509842696 | YES | MATCH |
| MergeX vs MergeXParam | Sorted | 10 | 7 | 18 | 18 | YES | 6326348811841823672 | 6326348811841823672 | YES | MATCH |
| QuickX vs QuickXParam | Sorted | 10 | 8 | 36 | 36 | YES | -4197516502587883249 | -4197516502587883249 | YES | MATCH |
| Merge vs MergeCutoff | Sorted | 50 | 1 | 627 | 627 | YES | 1806648906780468507 | 1806648906780468507 | YES | MATCH |
| Quick vs QuickCutoff | Sorted | 50 | 1 | 2548 | 2548 | YES | -6888469896776816828 | -6888469896776816828 | YES | MATCH |
| MergeX vs MergeXParam | Sorted | 50 | 7 | 98 | 98 | YES | 7109925251364189088 | 7109925251364189088 | YES | MATCH |
| QuickX vs QuickXParam | Sorted | 50 | 8 | 286 | 286 | YES | 5080741408036243794 | 5080741408036243794 | YES | MATCH |
| Merge vs MergeCutoff | Sorted | 100 | 1 | 1502 | 1502 | YES | 5743848855694259833 | 5743848855694259833 | YES | MATCH |
| Quick vs QuickCutoff | Sorted | 100 | 1 | 10098 | 10098 | YES | 4493579217371941918 | 4493579217371941918 | YES | MATCH |
| MergeX vs MergeXParam | Sorted | 100 | 7 | 198 | 198 | YES | -2074960925418093492 | -2074960925418093492 | YES | MATCH |
| QuickX vs QuickXParam | Sorted | 100 | 8 | 671 | 671 | YES | 7720323297257580285 | 7720323297257580285 | YES | MATCH |
| Merge vs MergeCutoff | Sorted | 500 | 1 | 10250 | 10250 | YES | 3357613509905873857 | 3357613509905873857 | YES | MATCH |
| Quick vs QuickCutoff | Sorted | 500 | 1 | 250498 | 250498 | YES | -8341360815853433834 | -8341360815853433834 | YES | MATCH |
| MergeX vs MergeXParam | Sorted | 500 | 7 | 998 | 998 | YES | -2905554777127166724 | -2905554777127166724 | YES | MATCH |
| QuickX vs QuickXParam | Sorted | 500 | 8 | 4377 | 4377 | YES | -1177137610913680938 | -1177137610913680938 | YES | MATCH |
| Merge vs MergeCutoff | Sorted | 1000 | 1 | 22998 | 22998 | YES | -7616532630906833430 | -7616532630906833430 | YES | MATCH |
| Quick vs QuickCutoff | Sorted | 1000 | 1 | 1000998 | 1000998 | YES | 3581608897714208780 | 3581608897714208780 | YES | MATCH |
| MergeX vs MergeXParam | Sorted | 1000 | 7 | 1998 | 1998 | YES | -7583380164703905960 | -7583380164703905960 | YES | MATCH |
| QuickX vs QuickXParam | Sorted | 1000 | 8 | 9750 | 9750 | YES | 5488597085291661056 | 5488597085291661056 | YES | MATCH |
| Merge vs MergeCutoff | Reverse | 10 | 1 | 65 | 65 | YES | -6715682103183665925 | -6715682103183665925 | YES | MATCH |
| Quick vs QuickCutoff | Reverse | 10 | 1 | 108 | 108 | YES | 6263670320010966060 | 6263670320010966060 | YES | MATCH |
| MergeX vs MergeXParam | Reverse | 10 | 7 | 52 | 52 | YES | 6718898218668851222 | 6718898218668851222 | YES | MATCH |
| QuickX vs QuickXParam | Reverse | 10 | 8 | 41 | 41 | YES | -7649964511605193473 | -7649964511605193473 | YES | MATCH |
| Merge vs MergeCutoff | Reverse | 50 | 1 | 607 | 607 | YES | 7294505700496951185 | 7294505700496951185 | YES | MATCH |
| Quick vs QuickCutoff | Reverse | 50 | 1 | 2548 | 2548 | YES | 1921779065381488148 | 1921779065381488148 | YES | MATCH |
| MergeX vs MergeXParam | Reverse | 50 | 7 | 540 | 540 | YES | -6600450073309340546 | -6600450073309340546 | YES | MATCH |
| QuickX vs QuickXParam | Reverse | 50 | 8 | 496 | 496 | YES | -3642719269209591675 | -3642719269209591675 | YES | MATCH |
| Merge vs MergeCutoff | Reverse | 100 | 1 | 1462 | 1462 | YES | -4961540409045017659 | -4961540409045017659 | YES | MATCH |
| Quick vs QuickCutoff | Reverse | 100 | 1 | 10098 | 10098 | YES | -766477871191657527 | -766477871191657527 | YES | MATCH |
| MergeX vs MergeXParam | Reverse | 100 | 7 | 1329 | 1329 | YES | -7010470534800870138 | -7010470534800870138 | YES | MATCH |
| QuickX vs QuickXParam | Reverse | 100 | 8 | 1646 | 1646 | YES | 3693246013963683480 | 3693246013963683480 | YES | MATCH |
| Merge vs MergeCutoff | Reverse | 500 | 1 | 10194 | 10194 | YES | 6699110394388291357 | 6699110394388291357 | YES | MATCH |
| Quick vs QuickCutoff | Reverse | 500 | 1 | 250498 | 250498 | YES | 3122200898609763289 | 3122200898609763289 | YES | MATCH |
| MergeX vs MergeXParam | Reverse | 500 | 7 | 9565 | 9565 | YES | -6745052100060015094 | -6745052100060015094 | YES | MATCH |
| QuickX vs QuickXParam | Reverse | 500 | 8 | 33346 | 33346 | YES | -5115409692297733856 | -5115409692297733856 | YES | MATCH |
| Merge vs MergeCutoff | Reverse | 1000 | 1 | 22886 | 22886 | YES | 4829629680605520882 | 4829629680605520882 | YES | MATCH |
| Quick vs QuickCutoff | Reverse | 1000 | 1 | 1000998 | 1000998 | YES | -3651691080828399379 | -3651691080828399379 | YES | MATCH |
| MergeX vs MergeXParam | Reverse | 1000 | 7 | 21629 | 21629 | YES | 7537584068831211721 | 7537584068831211721 | YES | MATCH |
| QuickX vs QuickXParam | Reverse | 1000 | 8 | 129221 | 129221 | YES | -4980313256478403992 | -4980313256478403992 | YES | MATCH |
| Merge vs MergeCutoff | Duplicates | 10 | 1 | 74 | 74 | YES | -3002263426308236574 | -3002263426308236574 | YES | MATCH |
| Quick vs QuickCutoff | Duplicates | 10 | 1 | 57 | 57 | YES | 2561961612444667224 | 2561961612444667224 | YES | MATCH |
| MergeX vs MergeXParam | Duplicates | 10 | 7 | 48 | 48 | YES | 3863676036601249059 | 3863676036601249059 | YES | MATCH |
| QuickX vs QuickXParam | Duplicates | 10 | 8 | 41 | 41 | YES | 9215717310216028070 | 9215717310216028070 | YES | MATCH |
| Merge vs MergeCutoff | Duplicates | 50 | 1 | 690 | 690 | YES | 3243223481368315157 | 3243223481368315157 | YES | MATCH |
| Quick vs QuickCutoff | Duplicates | 50 | 1 | 512 | 512 | YES | -9055869643669348121 | -9055869643669348121 | YES | MATCH |
| MergeX vs MergeXParam | Duplicates | 50 | 7 | 561 | 561 | YES | 884517367491001943 | 884517367491001943 | YES | MATCH |
| QuickX vs QuickXParam | Duplicates | 50 | 8 | 310 | 310 | YES | -4512136812734473970 | -4512136812734473970 | YES | MATCH |
| Merge vs MergeCutoff | Duplicates | 100 | 1 | 1662 | 1662 | YES | -8595331712245771569 | -8595331712245771569 | YES | MATCH |
| Quick vs QuickCutoff | Duplicates | 100 | 1 | 1332 | 1332 | YES | -2828024008789907974 | -2828024008789907974 | YES | MATCH |
| MergeX vs MergeXParam | Duplicates | 100 | 7 | 1397 | 1397 | YES | 7538758356631482841 | 7538758356631482841 | YES | MATCH |
| QuickX vs QuickXParam | Duplicates | 100 | 8 | 717 | 717 | YES | 5528454929387491673 | 5528454929387491673 | YES | MATCH |
| Merge vs MergeCutoff | Duplicates | 500 | 1 | 11625 | 11625 | YES | 3885651760080141012 | 3885651760080141012 | YES | MATCH |
| Quick vs QuickCutoff | Duplicates | 500 | 1 | 8580 | 8580 | YES | -3189699182496597797 | -3189699182496597797 | YES | MATCH |
| MergeX vs MergeXParam | Duplicates | 500 | 7 | 10127 | 10127 | YES | -8796804107850518373 | -8796804107850518373 | YES | MATCH |
| QuickX vs QuickXParam | Duplicates | 500 | 8 | 4676 | 4676 | YES | 8538848963410859987 | 8538848963410859987 | YES | MATCH |
| Merge vs MergeCutoff | Duplicates | 1000 | 1 | 26124 | 26124 | YES | -1740575681789287553 | -1740575681789287553 | YES | MATCH |
| Quick vs QuickCutoff | Duplicates | 1000 | 1 | 20351 | 20351 | YES | 7237247240750208331 | 7237247240750208331 | YES | MATCH |
| MergeX vs MergeXParam | Duplicates | 1000 | 7 | 23100 | 23100 | YES | -7254291183331992489 | -7254291183331992489 | YES | MATCH |
| QuickX vs QuickXParam | Duplicates | 1000 | 8 | 10862 | 10862 | YES | -2172380235116496720 | -2172380235116496720 | YES | MATCH |
| Merge vs MergeCutoff | AllEqual | 10 | 1 | 69 | 69 | YES | 1042182932674332476 | 1042182932674332476 | YES | MATCH |
| Quick vs QuickCutoff | AllEqual | 10 | 1 | 54 | 54 | YES | 798674791558867584 | 798674791558867584 | YES | MATCH |
| MergeX vs MergeXParam | AllEqual | 10 | 7 | 18 | 18 | YES | 5071814153876505472 | 5071814153876505472 | YES | MATCH |
| QuickX vs QuickXParam | AllEqual | 10 | 8 | 36 | 36 | YES | -8633285698009618688 | -8633285698009618688 | YES | MATCH |
| Merge vs MergeCutoff | AllEqual | 50 | 1 | 627 | 627 | YES | -5891701532080862532 | -5891701532080862532 | YES | MATCH |
| Quick vs QuickCutoff | AllEqual | 50 | 1 | 476 | 476 | YES | -2589123009755031296 | -2589123009755031296 | YES | MATCH |
| MergeX vs MergeXParam | AllEqual | 50 | 7 | 98 | 98 | YES | -6830537150336258176 | -6830537150336258176 | YES | MATCH |
| QuickX vs QuickXParam | AllEqual | 50 | 8 | 288 | 288 | YES | 212474906734442496 | 212474906734442496 | YES | MATCH |
| Merge vs MergeCutoff | AllEqual | 100 | 1 | 1502 | 1502 | YES | -8014983017390907264 | -8014983017390907264 | YES | MATCH |
| Quick vs QuickCutoff | AllEqual | 100 | 1 | 1143 | 1143 | YES | -5861937201721607236 | -5861937201721607236 | YES | MATCH |
| MergeX vs MergeXParam | AllEqual | 100 | 7 | 198 | 198 | YES | -5567508350697503104 | -5567508350697503104 | YES | MATCH |
| QuickX vs QuickXParam | AllEqual | 100 | 8 | 676 | 676 | YES | -7875860215560501504 | -7875860215560501504 | YES | MATCH |
| Merge vs MergeCutoff | AllEqual | 500 | 1 | 10250 | 10250 | YES | 4998218821157463424 | 4998218821157463424 | YES | MATCH |
| Quick vs QuickCutoff | AllEqual | 500 | 1 | 7951 | 7951 | YES | 7446602852464738748 | 7446602852464738748 | YES | MATCH |
| MergeX vs MergeXParam | AllEqual | 500 | 7 | 998 | 998 | YES | 879651204119674496 | 879651204119674496 | YES | MATCH |
| QuickX vs QuickXParam | AllEqual | 500 | 8 | 4408 | 4408 | YES | 8989751349720961536 | 8989751349720961536 | YES | MATCH |
| Merge vs MergeCutoff | AllEqual | 1000 | 1 | 22998 | 22998 | YES | 5430496077104677504 | 5430496077104677504 | YES | MATCH |
| Quick vs QuickCutoff | AllEqual | 1000 | 1 | 17884 | 17884 | YES | -1567829885414418176 | -1567829885414418176 | YES | MATCH |
| MergeX vs MergeXParam | AllEqual | 1000 | 7 | 1998 | 1998 | YES | -5159172713617087360 | -5159172713617087360 | YES | MATCH |
| QuickX vs QuickXParam | AllEqual | 1000 | 8 | 9812 | 9812 | YES | -6498229715866297600 | -6498229715866297600 | YES | MATCH |

## 3. Tổng kết:
- Tổng số phép thử so sánh: 300
- Số phép thử trùng khớp 100%: 300 / 300
- Trạng thái Gate 4: **ĐẠT (PASSED)** - Chứng minh biến thể trung thành 100% với bản gốc.
