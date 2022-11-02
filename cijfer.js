const maximalePunten = 65.25
for (let i = 0; i <= maximalePunten; i += .25) {
    const r = {}
    r.punten = i;
    r.cijfer = cijfer(i, maximalePunten, 7.323);
    console.log(r);
}

function cijfer(points, maxPoints, gokkans = 0) {
    return ((points - gokkans) / (maxPoints - gokkans)) * 11;
}