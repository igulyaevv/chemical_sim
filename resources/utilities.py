import time
from math import sqrt

from numpy.polynomial.polynomial import polyfit


def run_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(time.time()-start_time)
        return result
    return wrapper


def gist_compare(result_gist, theory_gist):
    if len(result_gist) == len(theory_gist):
        eps = sqrt(
            sum(
                (
                    list(result_gist.values())[i] ** 2 - list(theory_gist.values())[i] ** 2
                    for i in range(len(theory_gist))
                )
            )
        )
        print(eps)
    elif len(result_gist) > len(theory_gist):
        eps = set()
        for i in range(len(result_gist) - len(theory_gist) + 1):
            eps.add(
                sqrt(
                    sum(
                        (
                            (list(result_gist.values())[j + i] - list(theory_gist.values())[j]) ** 2
                            for j in range(len(theory_gist))
                        )
                    )
                )
            )
        eps = min(eps)
        print(eps)
    else:
        eps = 0  # добить до равенства или неравенства
        print(eps)

    koeff1 = polyfit(x=list(result_gist.keys()), y=list(result_gist.values()), deg=1)
    koeff2 = polyfit(x=list(theory_gist.keys()), y=list(theory_gist.values()), deg=1)
    print(koeff2)
    eps = sqrt(sum(((koeff1[0] - koeff2[0]) ** 2, (koeff1[1] - koeff2[1]) ** 2)))
    print(eps)
