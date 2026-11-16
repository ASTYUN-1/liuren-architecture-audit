import {sqlClient} from '/opt/wenheng/current/src/server/db.ts';
const db=sqlClient();
try{
 const [records]=await db`SELECT count(*)::int AS gatewayRecords,count(*) FILTER(WHERE is_test)::int AS adminTestRecords,count(*) FILTER(WHERE paid_at IS NOT NULL)::int AS confirmedPayments,count(*) FILTER(WHERE NOT is_test)::int AS customerPayments FROM gateway_payments`;
 const [orders]=await db`SELECT count(*)::int AS gatewayOrders FROM orders WHERE provider='nbzhifu'`;
 console.log(JSON.stringify({...records,...orders}));
}finally{await db.end()}
