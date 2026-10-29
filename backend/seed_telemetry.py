import asyncio
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select, delete
from app.database import SessionLocal
from app.models import Well, Telemetry

STEPS_PER_DAY = 144
DAYS = 7

def base_value(base, noise, amp=0.02):
    return base + base * amp * random.uniform(-1, 1) + random.gauss(0, noise)

async def seed():
    async with SessionLocal() as db:
        wells = (await db.execute(select(Well).order_by(Well.id))).scalars().all()
        if not wells:
            print('Net skvazhin')
            return
        wells = wells[:5]
        print(f'Generating for {len(wells)} wells: {[w.well_number for w in wells]}')
        well_ids = [w.id for w in wells]
        await db.execute(delete(Telemetry).where(Telemetry.well_id.in_(well_ids)))
        await db.commit()
        types = ['water_breakthrough','hydrate','pump_wear','none','water_breakthrough']
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=DAYS)
        total = 0
        for idx, well in enumerate(wells):
            anomaly = types[idx % len(types)]
            print(f'  Well {well.well_number} (id={well.id}): {anomaly}')
            p_before, t_before, p_after, t_after, p_bottom = 18.5, 67.0, 12.3, 55.2, 22.1
            q_gas, q_liq, water_cut, vib = 145.0, 5.0, 5.0, 3.0
            a_start = STEPS_PER_DAY * 4
            a_dur = STEPS_PER_DAY * 2
            for step in range(STEPS_PER_DAY * DAYS):
                ts = start + timedelta(minutes=10 * step)
                dep = 1 - 0.00005 * step
                qg = base_value(q_gas * dep, 1.5)
                ql = base_value(q_liq, 0.3)
                wc = water_cut
                vb = base_value(vib, 0.2)
                pa = base_value(p_after, 0.1)
                ta = base_value(t_after, 0.3)
                pb = base_value(p_before, 0.15)
                tb = base_value(t_before, 0.4)
                if a_start <= step < a_start + a_dur:
                    pr = (step - a_start) / a_dur
                    if anomaly == 'water_breakthrough':
                        wc = water_cut + 40 * pr
                        qg = qg * (1 - 0.5 * pr)
                        ql = q_liq + 30 * pr
                    elif anomaly == 'hydrate':
                        pa = pa * (1 + 0.4 * pr)
                        ta = ta * (1 - 0.3 * pr)
                    elif anomaly == 'pump_wear':
                        vb = vb + 8 * pr
                db.add(Telemetry(well_id=well.id, ts=ts,
                    pressure_before_choke=Decimal(f'{pb:.3f}'),
                    temperature_before_choke=Decimal(f'{tb:.2f}'),
                    pressure_after_choke=Decimal(f'{pa:.3f}'),
                    temperature_after_choke=Decimal(f'{ta:.2f}'),
                    bottomhole_pressure=Decimal(f'{base_value(p_bottom, 0.2):.3f}'),
                    flow_rate_gas=Decimal(f'{qg:.3f}'),
                    flow_rate_liquid=Decimal(f'{ql:.3f}'),
                    water_cut=Decimal(f'{wc:.2f}'),
                    vibration=Decimal(f'{vb:.3f}'),
                ))
                total += 1
                if total % 1000 == 0:
                    await db.commit()
                    print(f'  {total} points')
            await db.commit()
        print(f'Done: {total} points')

if __name__ == '__main__':
    asyncio.run(seed())