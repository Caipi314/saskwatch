import numpy as np


class FWI:
    def __init__(self, month=4):
        self.month = month
        self.F_0 = 85.0  # FFMC
        self.P_0 = 6.0  # DMC
        self.D_0 = 15.0  # DC

    def addDay(self, T, H, W, r_0):
        # T: temp, H: humidity, W: wind, r_0: rain
        F, m = self.getFFMC(self.F_0, r_0, H, T, W)
        P = self.getDMC(self.P_0, r_0, T, H)
        D = self.getDC(self.D_0, r_0, T)
        fwi = self.getFWI(W, m, P, D)

        self.F_0 = F
        self.P_0 = P
        self.D_0 = D
        return fwi

    def getFFMC(self, F_0, r_0, H, T, W):
        m_0 = 147.2 * (101 - F_0) / (59.5 + F_0)
        if r_0 > 0.5:
            r_f = r_0 - 0.5
            if m_0 <= 150:
                m_r = m_0 + 42.5 * r_f * np.exp(-100 / (251 - m_0)) * (
                    1 - np.exp(-6.93 / r_f)
                )
            else:
                m_r = (
                    m_0
                    + 42.5
                    * r_f
                    * np.exp(-100 / (251 - m_0))
                    * (1 - np.exp(-6.93 / r_f))
                    + 0.0015 * (m_0 - 150) ** 2 * r_f**0.5
                )

            m_0 = min(m_r, 250)  # clamp m_r < 250

        E_d = (
            0.942 * H**0.679
            + 11 * np.exp((H - 100) / 10)
            + 0.18 * (21.1 - T) * (1 - np.exp(-0.115 * H))
        )

        if m_0 > E_d:
            k_0 = 0.424 * (1 - (H / 100) ** 1.7) + 0.0694 * W**0.5 * (
                1 - (H / 100) ** 8
            )
            k_d = k_0 * 0.581 * np.exp(0.0365 * T)
            m = E_d + (m_0 - E_d) * 10 ** (-k_d)

        if m_0 < E_d:
            E_w = (
                0.618 * H**0.753
                + 10 * np.exp((H - 100) / 10)
                + 0.18 * (21.1 - T) * (1 - np.exp(-0.115 * H))
            )
            if m_0 < E_w:
                k_1 = 0.424 * (1 - ((100 - H) / 100) ** 1.7) + 0.0694 * W**0.5 * (
                    1 - ((100 - H) / 100) ** 8
                )
                k_w = k_1 * 0.581 * np.exp(0.0365 * T)
                m = E_w - (E_w - m_0) * 10 ** (-k_w)

            if E_d >= m_0 and m_0 >= E_w:
                m = m_0
        F = 59.5 * (250 - m) / (147.2 + m)
        return F, m

    def getDMC(self, P_0, r_0, T, H):
        L_edata = [6.5, 7.5, 9, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8, 7, 6]

        if r_0 > 1.5:
            r_e = 0.92 * r_0 - 1.27
            M_0 = 20 + np.exp(5.6348 - P_0 / 43.43)
            if P_0 <= 33:
                b = 100 / (0.5 + 0.3 * P_0)
            elif P_0 > 65:
                b = 6.2 * np.log(P_0) - 17.2
            else:
                b = 14 - 1.3 * np.log(P_0)

            M_r = M_0 + 1000 * r_e / (48.77 + b * r_e)
            P_r = 244.72 - 43.43 * np.log(M_r - 20)
            P_0 = max(P_r, 0)  # clamp to >0

        L_e = L_edata[self.month]
        T = max(T, -1.1)  # clamp to >-1.1
        K = 1.894 * (T + 1.1) * (100 - H) * L_e * 10 ** (-6)
        P = P_0 + 100 * K
        return P

    def getDC(self, D_0, r_0, T):
        L_fdata = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5, 2.4, 0.4, -1.6, -1.6]

        if r_0 > 2.8:
            r_d = 0.83 * r_0 - 1.27
            Q_0 = 800 * np.exp(-D_0 / 400)
            Q_r = Q_0 + 3.937 * r_d
            D_r = 400 * np.log(800 / Q_r)
            D_r = max(D_r, 0)  # clamp to >0
            D_0 = D_r

        T = max(T, -2.8)  # clamp to >-2.8
        V = 0.36 * (T + 2.8) + L_fdata[self.month]
        V = max(V, 0)  # clamp to V > 0
        D = D_0 + 0.5 * V
        return D

    def getFWI(self, W, m, P, D):
        fW = np.exp(0.05039 * W)
        fF = 91.9 * np.exp(-0.1386 * m) * (1 + (m**5.31) / (4.93 * 10**7))
        R = 0.208 * fW * fF

        if P > 0.4 * D:
            U = P - (1 - 0.8 * D / (P + 0.4 * D)) * (0.92 + (0.0114 * P) ** 1.7)
        else:
            U = 0.8 * P * D / (P + 0.4 * D)

        if U > 80:
            fD = 1000 / (25 + 108.64 * np.exp(-0.023 * U))
        else:
            fD = 0.626 * U**0.809 + 2

        B = 0.1 * R * fD

        if B > 1:
            S = np.exp(2.72 * (0.434 * np.log(B)) ** 0.647)
        else:
            S = B

        # U: today's BUI
        # R: today's ISI
        return S


days = [
    [17.0000, 42.0000, 25.0000, 0],
    [20.0000, 21.0000, 25.0000, 2.4000],
    [8.5000, 40.0000, 17.0000, 0],
    [6.5000, 25.0000, 6.0000, 0],
    [13.0000, 34.0000, 24.0000, 0],
    [6.0000, 40.0000, 22.0000, 0.4000],
    [5.5000, 52.0000, 6.0000, 0],
    [8.5000, 46.0000, 16.0000, 0],
    [9.5000, 54.0000, 20.0000, 0],
    [7.0000, 93.0000, 14.0000, 9.0000],
    [6.5000, 71.0000, 17.0000, 1.0000],
    [6.0000, 59.0000, 17.0000, 0],
    [13.0000, 52.0000, 4.0000, 0],
    [15.5000, 40.0000, 11.0000, 0],
    [23.0000, 25.0000, 9.0000, 0],
    [19.0000, 46.0000, 16.0000, 0],
]
# fwi = FWI(month=3)
# for day in days:
#     newFwi = fwi.addDay(day[0], day[1], day[2], day[3])
#     print(newFwi)


# p1 = FWI("John", 36)

# print(p1.name)
# print(p1.age)
