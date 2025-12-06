import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 1,           // será sobrescrito na linha de comando
  iterations: 1,    // idem
};

const img = open('test.jpg', 'b');

export default function () {
  const formData = {
    file: http.file(img, 'test.jpg', 'image/jpeg'),
    k: __ENV.K,                       // vem via linha de comando
    adicionarImgAoDb: 'false',
  };

  const res = http.post(__ENV.URL, formData);

  check(res, {
    'status 200': (r) => r.status === 200,
  });
}
