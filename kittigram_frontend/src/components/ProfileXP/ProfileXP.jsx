import React, { useEffect, useState } from "react";
import { getProfile } from "../../utils/api";
import "./ProfileXP.css";

function ProfileXP() {
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const loadProfile = () => {
    setIsLoading(true);
    setError("");

    getProfile()
      .then((data) => {
        setProfile(data);
      })
      .catch(() => {
        setError("Не удалось загрузить XP-профиль");
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  useEffect(() => {
    loadProfile();
  }, []);

  if (isLoading) {
    return (
      <section className="profile-xp">
        <p className="profile-xp__text">Загрузка профиля...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="profile-xp">
        <p className="profile-xp__error">{error}</p>
        <button className="profile-xp__button" onClick={loadProfile}>
          Повторить
        </button>
      </section>
    );
  }

  if (!profile) {
    return null;
  }

  const progressPercent = Math.min(profile.current_level_xp, 100);

  return (
    <section className="profile-xp">
      <div className="profile-xp__header">
        <div>
          <h2 className="profile-xp__title">Мой профиль</h2>
          <p className="profile-xp__username">{profile.username}</p>
        </div>

        <div className="profile-xp__level">
          <span className="profile-xp__level-number">{profile.level}</span>
          <span className="profile-xp__level-text">уровень</span>
        </div>
      </div>

      <div className="profile-xp__stats">
        <div className="profile-xp__stat">
          <span className="profile-xp__stat-value">{profile.xp}</span>
          <span className="profile-xp__stat-label">XP всего</span>
        </div>

        <div className="profile-xp__stat">
          <span className="profile-xp__stat-value">
            {profile.xp_to_next_level}
          </span>
          <span className="profile-xp__stat-label">до уровня</span>
        </div>
      </div>

      <div className="profile-xp__progress">
        <div className="profile-xp__progress-line">
          <div
            className="profile-xp__progress-fill"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <p className="profile-xp__progress-text">
          {profile.current_level_xp} / 100 XP до следующего уровня
        </p>
      </div>

      <div className="profile-xp__events">
        <h3 className="profile-xp__subtitle">Последние начисления</h3>

        {profile.recent_events && profile.recent_events.length > 0 ? (
          <ul className="profile-xp__event-list">
            {profile.recent_events.map((event) => (
              <li className="profile-xp__event" key={event.id}>
                <span>{event.action_display || event.action}</span>
                <strong>+{event.points} XP</strong>
              </li>
            ))}
          </ul>
        ) : (
          <p className="profile-xp__text">
            Пока нет начислений. Создай кота, чтобы получить первый XP.
          </p>
        )}
      </div>

      <button className="profile-xp__button" onClick={loadProfile}>
        Обновить профиль
      </button>
    </section>
  );
}

export default ProfileXP;