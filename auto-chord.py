import sys
# autochord 패키지가 위치한 src 폴더를 sys.path에 추가합니다.
sys.path.insert(0, '/app/autochord-0.1.4/src')

# 이제 autochord 패키지를 정상적으로 임포트할 수 있습니다.
from autochord import recognize

import math
import time

start = time.time()
recognize('source/dont_lazy.wav', lab_fn='source/dont_lazy.lab')
end = time.time()

print(f"{end - start:.5f} sec")